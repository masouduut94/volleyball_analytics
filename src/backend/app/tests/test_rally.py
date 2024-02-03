import unittest

from src.backend.app.schemas.rallies import RallyBaseSchema
from src.backend.app.db.engine import Base, engine, get_db
from fastapi.testclient import TestClient
from src.backend.app.app import app

"""
match_id
sets
spikes
blocks
receives
service
ball_positions
team1_positions
team2_positions
rally_states
result
start_frame
end_frame
clip_path

"""


class RallyTest(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        app.dependency_overrides[get_db] = get_db
        self.client = TestClient(app)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    def test_get_one_rally(self):
        # Testing rally creation and fetching for one rally.
        t = RallyBaseSchema(name='canada', is_national_rally=True)
        response = self.client.post("/api/rallies/", json=t.model_dump())
        self.assertEqual(response.status_code, 201)

        rally_output = response.json()
        rally_output = RallyBaseSchema(**rally_output)
        response = self.client.get(f"/api/rallies/{rally_output.id}")
        self.assertEqual(response.status_code, 200)

    def test_update_rally(self):
        # Testing rally creation and fetching for one rally.
        t = RallyBaseSchema(name='canada', is_national_rally=True)
        r = self.client.post("/api/rallies/", json=t.model_dump())
        t = RallyBaseSchema(**r.json())

        t.name = 'IRAN'
        _ = self.client.put(f"/api/rallies/{t.id}", json=t.model_dump())
        r = self.client.get(f"/api/rallies/{t.id}")
        output = r.json()
        self.assertEqual(output['name'], t.name)
        self.assertEqual(r.status_code, 200)

    def test_delete_rally(self):
        # Testing rally creation and fetching for one rally.
        t = RallyBaseSchema(name='canada', is_national_rally=True)
        r = self.client.post("/api/rallies/", json=t.model_dump())
        t = RallyBaseSchema(**r.json())

        f = self.client.delete(f"/api/rallies/{t.id}")
        self.assertEqual(f.status_code, 200)

        r = self.client.get(f"/api/rallies/{t.id}")
        self.assertEqual(r.status_code, 404)

    def test_get_all_rallies(self):
        # Testing rally creation and fetching for multiple rally.
        t = RallyBaseSchema(name='canada', is_national_rally=True)
        e = RallyBaseSchema(name='usa', is_national_rally=True)
        response = self.client.post(f"/api/rallies/", json=e.model_dump())
        response = self.client.post(f"/api/rallies/", json=t.model_dump())

        response = self.client.get(f"/api/rallies/")
        js = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(js), 2)
