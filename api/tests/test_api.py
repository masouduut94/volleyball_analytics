from fastapi.testclient import TestClient
from api.rest import app
from api.models import Match
from api.schemas import MatchData
import unittest


class MatchTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_matches(self):
        match_id = 1
        response = self.client.get(f"/match/{match_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn('team1_id', dict(response.json()))

    
