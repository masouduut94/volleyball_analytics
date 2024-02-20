from src.backend.app.schemas.players import PlayerBaseSchema, PlayerCreateSchema
from src.backend.app.tests.utility import VBTest
from src.backend.app.enums.enums import VolleyBallPositions as pos


class PlayerTest(VBTest):

    def test_get_one_player(self):
        # Testing player creation and fetching for one player.
        nation = self.create_nation(name="United States of America", display_name="USA")
        team = self.create_team(name='USA')
        player = PlayerCreateSchema(first_name='Benjamin', last_name='Patch', role=pos.OPPOSITE_HITTER, height=202,
                                    weight=84, nation_id=nation.id, team_id=team.id)
        response = self.client.post("/api/players/", json=player.model_dump())
        self.assertEqual(response.status_code, 201)

        player_output = response.json()
        player_output = PlayerBaseSchema(**player_output)
        response = self.client.get(f"/api/players/{player_output.id}")
        self.assertEqual(response.status_code, 200)

    def test_get_all_players(self):
        # Testing player creation and fetching for multiple player.
        nation = self.create_nation(name="United States of America", display_name="USA")
        team = self.create_team(name='USA')
        benjamin = PlayerCreateSchema(first_name='Benjamin', last_name='Patch', role=pos.OUTSIDE_HITTER, height=202,
                                      weight=84, nation_id=nation.id, team_id=team.id)
        tony = PlayerCreateSchema(first_name='Tony', last_name='Defalco', role=pos.OPPOSITE_HITTER, height=202,
                                  weight=84, nation_id=nation.id, team_id=team.id)

        _ = self.client.post("/api/players/", json=benjamin.model_dump())
        _ = self.client.post("/api/players/", json=tony.model_dump())

        response = self.client.get("/api/players/")
        js = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(js), 2)

    def test_update_player(self):
        # Testing player creation and fetching for one player.
        nation = self.create_nation(name="United States of America", display_name="USA")
        team = self.create_team(name='USA')
        player = PlayerCreateSchema(first_name='Benjamin', last_name='Patch', role=pos.OPPOSITE_HITTER, height=202,
                                    weight=84, nation_id=nation.id, team_id=team.id)
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
        nation = self.create_nation(name="United States of America", display_name="USA")
        team = self.create_team(name='USA')
        player = PlayerCreateSchema(first_name='Benjamin', last_name='Patch', role=pos.OPPOSITE_HITTER, height=202,
                                    weight=84, nation_id=nation.id, team_id=team.id)
        resp = self.client.post("/api/players/", json=player.model_dump())
        player = PlayerBaseSchema(**resp.json())

        f = self.client.delete(f"/api/players/{player.id}")
        self.assertEqual(f.status_code, 200)

        resp = self.client.get(f"/api/players/{player.id}")
        self.assertEqual(resp.status_code, 404)
