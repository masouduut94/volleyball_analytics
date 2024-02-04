import unittest

from src.backend.app.schemas.players import PlayerBaseSchema, PlayerCreateSchema
from src.backend.app.schemas import teams, nations
from src.backend.app.db.engine import Base, engine, get_db
from fastapi.testclient import TestClient
from src.backend.app.app import app

"""
Testing Players
first_name
last_name
is_male
is_right_handed
role
height
weight
nation_id
club_id
"""


class PlayerTest(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        app.dependency_overrides[get_db] = get_db
        self.client = TestClient(app)

    def create_team(self) -> teams.TeamCreateSchema:
        team = teams.TeamCreateSchema(name='USA national team', is_national_team=True)
        r = self.client.post('/api/teams/', json=team.model_dump())
        team = teams.TeamBaseSchema(**r.json())
        return team

    def create_nation(self) -> nations.NationBaseSchema:
        nation = nations.NationCreateSchema(name='United States of America', display_name='USA')
        r = self.client.post('/api/nations/', json=nation.model_dump())
        nation = nations.NationBaseSchema(**r.json())
        return nation

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    def test_get_one_player(self):
        # Testing player creation and fetching for one player.
        nation = self.create_nation()
        team = self.create_team()
        player = PlayerCreateSchema(first_name='Benjamin', last_name='Patch', role='OH', height=202, weight=84,
                                    nation_id=nation.id, team_id=team.id)
        response = self.client.post("/api/players/", json=player.model_dump())
        self.assertEqual(response.status_code, 201)

        player_output = response.json()
        player_output = PlayerBaseSchema(**player_output)
        response = self.client.get(f"/api/players/{player_output.id}")
        self.assertEqual(response.status_code, 200)

    def test_get_all_players(self):
        # Testing player creation and fetching for multiple player.
        nation = self.create_nation()
        team = self.create_team()
        benjamin = PlayerCreateSchema(first_name='Benjamin', last_name='Patch', role='OH', height=202, weight=84,
                                      nation_id=nation.id, team_id=team.id)
        tony = PlayerCreateSchema(first_name='Tony', last_name='Defalco', role='OH', height=202, weight=84,
                                  nation_id=nation.id, team_id=team.id)

        _ = self.client.post(f"/api/players/", json=benjamin.model_dump())
        _ = self.client.post(f"/api/players/", json=tony.model_dump())

        response = self.client.get(f"/api/players/")
        js = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(js), 2)

    def test_update_player(self):
        # Testing player creation and fetching for one player.
        nation = self.create_nation()
        team = self.create_team()
        player = PlayerCreateSchema(first_name='Benjamin', last_name='Patch', role='OH', height=202, weight=84,
                                    nation_id=nation.id, team_id=team.id)
        resp = self.client.post("/api/players/", json=player.model_dump())
        player = PlayerBaseSchema(**resp.json())

        player.first_name = 'Tony'
        player.last_name = 'Defalco'
        _ = self.client.put(f"/api/players/{player.id}", json=player.model_dump())
        resp = self.client.get(f"/api/players/{player.id}")
        output = resp.json()
        self.assertEqual(output['first_name'], player.first_name)
        self.assertEqual(resp.status_code, 200)

    def test_delete_player(self):
        # Testing player creation and fetching for one player.
        nation = self.create_nation()
        team = self.create_team()
        player = PlayerCreateSchema(first_name='Benjamin', last_name='Patch', role='OH', height=202, weight=84,
                                    nation_id=nation.id, team_id=team.id)
        resp = self.client.post("/api/players/", json=player.model_dump())
        player = PlayerBaseSchema(**resp.json())

        f = self.client.delete(f"/api/players/{player.id}")
        self.assertEqual(f.status_code, 200)

        resp = self.client.get(f"/api/players/{player.id}")
        self.assertEqual(resp.status_code, 404)
