from src.backend.app.schemas.nations import NationBaseSchema
from src.backend.app.tests.utility import VBTest


class NationTest(VBTest):
    def test_get_one_team(self):
        # Testing team creation and fetching for one team.
        t = NationBaseSchema(name='canada', display_name="canada")
        response = self.client.post("/api/nations/", json=t.model_dump())
        self.assertEqual(response.status_code, 201)

        team_output = response.json()
        team_output = NationBaseSchema(**team_output)
        response = self.client.get(f"/api/nations/{team_output.id}")
        self.assertEqual(response.status_code, 200)

    def test_update_team(self):
        # Testing team creation and fetching for one team.
        t = NationBaseSchema(name='canada', display_name="canada")
        r = self.client.post("/api/nations/", json=t.model_dump())
        t = NationBaseSchema(**r.json())

        t.name = 'IRAN'
        _ = self.client.put(f"/api/nations/{t.id}", json=t.model_dump())
        r = self.client.get(f"/api/nations/{t.id}")
        output = r.json()
        self.assertEqual(output['name'], t.name)
        self.assertEqual(r.status_code, 200)

    def test_delete_team(self):
        # Testing team creation and fetching for one team.
        t = NationBaseSchema(name='canada', display_name="canada")
        r = self.client.post("/api/nations/", json=t.model_dump())
        t = NationBaseSchema(**r.json())

        f = self.client.delete(f"/api/nations/{t.id}")
        self.assertEqual(f.status_code, 200)

        r = self.client.get(f"/api/nations/{t.id}")
        self.assertEqual(r.status_code, 404)

    def test_get_all_teams(self):
        # Testing team creation and fetching for multiple team.
        t = NationBaseSchema(name='canada', display_name="canada")
        e = NationBaseSchema(name='canada', display_name="canada")
        response = self.client.post("/api/nations/", json=e.model_dump())
        response = self.client.post("/api/nations/", json=t.model_dump())

        response = self.client.get("/api/nations/")
        js = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(js), 2)
