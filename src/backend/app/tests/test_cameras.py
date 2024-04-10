from src.backend.app.schemas.cameras import CameraBaseSchema, CameraCreateSchema
from src.backend.app.tests.utility import VBTest


class CameraTest(VBTest):
    def test_get_one_camera(self):
        # Testing camera creation and fetching for one camera.
        t = CameraCreateSchema(angle_name='behind_team1')
        response = self.client.post("/api/cameras/", json=t.model_dump())
        self.assertEqual(response.status_code, 201)

        camera_output = response.json()
        camera_output = CameraBaseSchema(**camera_output)
        response = self.client.get(f"/api/cameras/{camera_output.id}")
        self.assertEqual(response.status_code, 200)

    def test_get_all_cameras(self):
        # Testing camera creation and fetching for multiple camera.
        t = CameraCreateSchema(angle_name='behind_team1')
        e = CameraCreateSchema(angle_name='behind_team2')
        response = self.client.post("/api/cameras/", json=e.model_dump())
        response = self.client.post("/api/cameras/", json=t.model_dump())

        response = self.client.get("/api/cameras/")
        js = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(js), 2)

    def test_update_camera(self):
        # Testing camera creation and fetching for one camera.
        t = CameraCreateSchema(angle_name='behind_team1')
        r = self.client.post("/api/cameras/", json=t.model_dump())
        t = CameraBaseSchema(**r.json())

        t.angle_name = 'side_camera'
        _ = self.client.put(f"/api/cameras/{t.id}", json=t.model_dump())
        r = self.client.get(f"/api/cameras/{t.id}")
        output = r.json()
        self.assertEqual(output['angle_name'], t.angle_name)
        self.assertEqual(r.status_code, 200)

    def test_delete_camera(self):
        # Testing camera creation and fetching for one camera.
        t = CameraCreateSchema(angle_name='behind_team1')
        r = self.client.post("/api/cameras/", json=t.model_dump())
        t = CameraBaseSchema(**r.json())

        f = self.client.delete(f"/api/cameras/{t.id}")
        self.assertEqual(f.status_code, 200)

        r = self.client.get(f"/api/cameras/{t.id}")
        self.assertEqual(r.status_code, 404)
