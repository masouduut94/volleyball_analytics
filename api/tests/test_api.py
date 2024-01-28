import unittest

from fastapi.testclient import TestClient
from api.rest import app
from api.schemas import TeamData

client = TestClient(app)


class TestTeam(unittest.TestCase):
    #
    # def tearDown(self) -> None:
    #     # Drop the tables in the test database
    #     Base.metadata.drop_all(bind=engine)

    # def test_get_team(self):
    #     # Base.metadata.create_all(bind=engine)
    #     t = TeamData(name='canada', is_national_team=True)
    #     response1 = client.post(f"/team/", json=t.model_dump_json())
    #     assert response1.status_code == 200
    #     f = response1.json()
    #     # nation = Nation.save(**n.model_dump())
    #     response = client.get(f"/team/{f.id}")
    #     self.assertEqual(response.status_code, 200)
        # self.assertIn('team1_id', dict(response.json()))

    def test_get_all_teams(self):
        # Base.metadata.create_all(bind=engine)
        # t = TeamData(name='canada', is_national_team=True)
        # response1 = client.post(f"/team/", json=t.model_dump_json())
        # assert response1.status_code == 200
        # f = response1.json()
        # nation = Nation.save(**n.model_dump())
        response = client.get(f"/team/")
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()




