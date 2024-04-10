from src.backend.app.schemas.videos import VideoBaseSchema
from src.backend.app.tests.utility import VBTest
from src.backend.app.schemas.cameras import CameraCreateSchema, CameraBaseSchema


class VideoTest(VBTest):
    def test_post_video_with_no_camera_inserted(self):
        # Testing video creation and fetching for one video.
        v = VideoBaseSchema(camera_type=1, path='/videos/file.mp4')
        response = self.client.post("/api/videos/", json=v.model_dump())
        self.assertEqual(response.status_code, 406)

    def test_get_all_videos(self):
        # Testing video creation and fetching for multiple video.
        c = CameraCreateSchema(angle_name="behind_team_1")
        response = self.client.post("/api/cameras/", json=c.model_dump())
        c = CameraBaseSchema(**response.json())

        v1 = VideoBaseSchema(camera_type_id=c.id, path='/videos/file.mp4')
        v2 = VideoBaseSchema(camera_type_id=c.id, path='/videos/file1.mp4')

        response = self.client.post("/api/videos/", json=v1.model_dump())
        response = self.client.post("/api/videos/", json=v2.model_dump())

        response = self.client.get("/api/videos/")
        js = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(js), 2)

    def test_get_one_video(self):
        # Testing video creation and fetching for one video.
        c = CameraCreateSchema(angle_name="behind_team_1")
        response = self.client.post("/api/cameras/", json=c.model_dump())
        self.assertEqual(response.status_code, 201)
        c = CameraBaseSchema(**response.json())

        v = VideoBaseSchema(camera_type_id=c.id, path='/videos/file.mp4')
        response = self.client.post("/api/videos/", json=v.model_dump())
        self.assertEqual(response.status_code, 201)

        video_output = response.json()
        video_output = VideoBaseSchema(**video_output)
        response = self.client.get(f"/api/videos/{video_output.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['camera_type_id'], c.id)

    def test_update_video(self):
        # Testing video creation and fetching for one video.
        c = CameraCreateSchema(angle_name="behind_team_1")
        response = self.client.post("/api/cameras/", json=c.model_dump())
        c = CameraBaseSchema(**response.json())
        v = VideoBaseSchema(camera_type_id=c.id, path='/videos/file.mp4')
        r = self.client.post("/api/videos/", json=v.model_dump())
        v = VideoBaseSchema(**r.json())

        v.path = '/videos/file222222.mp4'
        _ = self.client.put(f"/api/videos/{v.id}", json=v.model_dump())
        r = self.client.get(f"/api/videos/{v.id}")
        output = r.json()
        self.assertEqual(output['path'], v.path)
        self.assertEqual(r.status_code, 200)

    def test_delete_video(self):
        # Testing video creation and fetching for one video.
        c = CameraCreateSchema(angle_name="behind_team_1")
        response = self.client.post("/api/cameras/", json=c.model_dump())
        c = CameraBaseSchema(**response.json())
        v = VideoBaseSchema(camera_type_id=c.id, path='/videos/file.mp4')
        r = self.client.post("/api/videos/", json=v.model_dump())
        v = VideoBaseSchema(**r.json())

        f = self.client.delete(f"/api/videos/{v.id}")
        self.assertEqual(f.status_code, 200)

        r = self.client.get(f"/api/videos/{v.id}")
        self.assertEqual(r.status_code, 404)
