import unittest

from src.backend.app.schemas.players import PlayerBaseSchema
from src.backend.app.db.engine import Base, engine, get_db
from fastapi.testclient import TestClient
from src.backend.app.app import app

"""
Testing Match
    team1_id
    team2_id
    series_id
    video_id
"""


class PlayerTest(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        app.dependency_overrides[get_db] = get_db
        self.client = TestClient(app)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    def test_get_one_match(self):
        # Testing match creation and fetching for one match.
        t = MatchBaseSchema()
        response = self.client.post("/api/matches/", json=t.model_dump())
        self.assertEqual(response.status_code, 201)

        match_output = response.json()
        match_output = MatchBaseSchema(**match_output)
        response = self.client.get(f"/api/matches/{match_output.id}")
        self.assertEqual(response.status_code, 200)

    def test_update_match(self):
        # Testing match creation and fetching for one match.
        t = MatchBaseSchema()
        r = self.client.post("/api/matches/", json=t.model_dump())
        t = MatchBaseSchema(**r.json())

        t.name = 'IRAN'
        _ = self.client.put(f"/api/matches/{t.id}", json=t.model_dump())
        r = self.client.get(f"/api/matches/{t.id}")
        output = r.json()
        self.assertEqual(output['name'], t.name)
        self.assertEqual(r.status_code, 200)

    def test_delete_match(self):
        # Testing match creation and fetching for one match.
        t = MatchBaseSchema()
        r = self.client.post("/api/matches/", json=t.model_dump())
        t = MatchBaseSchema(**r.json())

        f = self.client.delete(f"/api/matches/{t.id}")
        self.assertEqual(f.status_code, 200)

        r = self.client.get(f"/api/matches/{t.id}")
        self.assertEqual(r.status_code, 404)

    def test_get_all_matches(self):
        # Testing match creation and fetching for multiple match.
        t = MatchBaseSchema()
        e = MatchBaseSchema()
        response = self.client.post(f"/api/matches/", json=e.model_dump())
        response = self.client.post(f"/api/matches/", json=t.model_dump())

        response = self.client.get(f"/api/matches/")
        js = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(js), 2)
