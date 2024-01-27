import unittest

from fastapi.testclient import TestClient
from api.rest import app
from api.database import db_setup, Base, Team, Nation, Player, Series, Camera, Match, Video, Rally
from api.schemas import MatchData, NationData

mode = 'test'
client = TestClient(app)

Session, engine = db_setup(mode=mode)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


class TestCase(unittest.TestCase):
    #
    # def tearDown(self) -> None:
    #     # Drop the tables in the test database
    #     Base.metadata.drop_all(bind=engine)

    def test_get_matches(self):
        # Base.metadata.create_all(bind=engine)
        n = NationData(name='wfwafa', display_name='USA')
        nation = Nation(**n.model_dump())
        # nation = Nation.save(**n.model_dump())
        response = client.get(f"/match/{nation.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn('team1_id', dict(response.json()))


if __name__ == '__main__':
    unittest.main()




