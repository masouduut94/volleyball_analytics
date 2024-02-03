import unittest

from src.backend.app.schemas.teams import TeamBaseSchema
from fastapi.testclient import TestClient
from src.backend.app.db.engine import Base, engine, get_db
from src.backend.app.app import app


class TeamTest(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        app.dependency_overrides[get_db] = get_db
        self.client = TestClient(app)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    def test_get_team(self):
        # Base.metadata.create_all(bind=engine)
        t = TeamBaseSchema(name='canada', is_national_team=True)
        response = self.client.post("/api/teams/", json=t.model_dump())
        self.assertEqual(response.status_code, 201)

        team_output = response.json()
        team_output = TeamBaseSchema(**team_output)
        response = self.client.get(f"/api/teams/{team_output.id}")
        self.assertEqual(response.status_code, 200)

    def test_get_all_teams(self):
        t = TeamBaseSchema(name='canada', is_national_team=True)
        response = self.client.post(f"/api/teams/", json=t.model_dump())
        self.assertEqual(response.status_code, 201)

        response = self.client.get(f"/api/teams/")
        self.assertEqual(response.status_code, 200)
