from src.backend.app.schemas.teams import TeamBaseSchema
from src.backend.app.tests.utility import VBTest


class TeamTest(VBTest):
    def test_get_one_team(self):
        # Testing team creation and fetching for one team.
        t = TeamBaseSchema(name='canada', is_national_team=True)
        response = self.client.post("/api/teams/", json=t.model_dump())
        self.assertEqual(response.status_code, 201)

        team_output = response.json()
        team_output = TeamBaseSchema(**team_output)
        response = self.client.get(f"/api/teams/{team_output.id}")
        self.assertEqual(response.status_code, 200)

    def test_get_all_teams(self):
        # Testing team creation and fetching for multiple team.
        t = TeamBaseSchema(name='canada', is_national_team=True)
        e = TeamBaseSchema(name='usa', is_national_team=True)
        response = self.client.post("/api/teams/", json=e.model_dump())
        response = self.client.post("/api/teams/", json=t.model_dump())

        response = self.client.get("/api/teams/")
        js = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(js), 2)

    def test_update_team(self):
        # Testing team creation and fetching for one team.
        t = TeamBaseSchema(name='canada', is_national_team=True)
        r = self.client.post("/api/teams/", json=t.model_dump())
        t = TeamBaseSchema(**r.json())

        t.name = 'IRAN'
        _ = self.client.put(f"/api/teams/{t.id}", json=t.model_dump())
        r = self.client.get(f"/api/teams/{t.id}")
        output = r.json()
        self.assertEqual(output['name'], t.name)
        self.assertEqual(r.status_code, 200)

    def test_delete_team(self):
        # Testing team creation and fetching for one team.
        t = TeamBaseSchema(name='canada', is_national_team=True)
        r = self.client.post("/api/teams/", json=t.model_dump())
        t = TeamBaseSchema(**r.json())

        f = self.client.delete(f"/api/teams/{t.id}")
        self.assertEqual(f.status_code, 200)

        r = self.client.get(f"/api/teams/{t.id}")
        self.assertEqual(r.status_code, 404)
