import unittest

from api.main import app
from api.schemas import RallyBaseSchema
from fastapi.testclient import TestClient
from api.database import Base, engine, get_db


class RallyTest(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        app.dependency_overrides[get_db] = get_db
        self.client = TestClient(app)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    def test_get_main(self):
        response1 = self.client.get("/")
        assert response1.status_code == 200

    def test_get_post_delete_team(self):
        # Test if the rally inserts, fetches, and removes...
        pass

    def test_get_multiple_rallies(self):
        pass

    def test_fetch_spikes_sets(self):
        pass

    #     # Base.metadata.create_all(bind=engine)
    #     t = RallyBaseSchema(name='canada', is_national_team=True)
    #     response = self.client.post("/team/", json=t.model_dump(exclude={'id'}))
    #     self.assertEqual(response.status_code, 201)
    #
    #     team_output = response.json()
    #     team_output = RallyBaseSchema(**team_output)
    #     response = self.client.get(f"/team/{team_output.id}")
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_get_all_teams(self):
    #     t = RallyBaseSchema(name='canada', is_national_team=True)
    #     response = self.client.post(f"/team/", json=t.model_dump(exclude={'id'}))
    #     self.assertEqual(response.status_code, 201)
    #
    #     response = self.client.get(f"/team/")
    #     self.assertEqual(response.status_code, 200)