from pydantic import ValidationError

from src.backend.app.tests.utility import VBTest
from src.backend.app.schemas import rallies
from src.backend.app.schemas import matches
from fastapi import status
import pendulum


class RallyTest(VBTest):
    def test_get_one_rally(self):
        # Testing rally creation and fetching for one rally.
        cam = self.create_camera(angle_name='behind_1')
        vid = self.create_video(camera_type_id=cam.id, path='ss.mp4')
        team1 = self.create_team(name='usa')
        team2 = self.create_team(name='canada')
        st_date = pendulum.now().subtract(weeks=2, days=3)
        end_date = pendulum.now()

        tournament = self.create_series(
            host='netherlands',
            start_date=st_date.to_iso8601_string(),
            end_date=end_date.to_iso8601_string()
        )
        match = matches.MatchCreateSchema(
            video_id=vid.id, series_id=tournament.id, team1_id=team1.id, team2_id=team2.id
        )
        response = self.client.post("/api/matches/", json=match.model_dump())
        self.assertEqual(response.status_code, 201, msg="match creation error")
        match_output = response.json()
        match = matches.MatchBaseSchema(**match_output)
        rally_input = rallies.RallyCreateSchema(
            match_id=match.id,
            start_frame=20,
            end_frame=100,
            order=1,
            clip_path='/mnt/videos/clip_1.mp4'
        )
        response = self.client.post("/api/rallies/", json=rally_input.model_dump())
        self.assertEqual(response.status_code, 201, msg="rally creation error")

        rally_output = response.json()
        rally_output = rallies.RallyBaseSchema(**rally_output)
        response = self.client.get(f"/api/rallies/{rally_output.id}")
        self.assertEqual(response.status_code, 200, msg="the rally was not found...")

    def test_update_rally(self):
        # Testing rally creation and fetching for one rally.
        match = self.create_match()

        # Start frame must be less than end frame...
        with self.assertRaises(ValidationError):
            _ = self.create_rally(
                match=match,
                clip_path='/mnt/disk1/video1.mp4',
                start_frame=500,
                end_frame=200,
                order=1
            )

        rally = self.create_rally(
            match=match,
            clip_path='/mnt/disk1/video1.mp4',
            start_frame=100,
            end_frame=200,
            order=1
        )

        rally.clip_path = '/mnt/video222222.webm'
        _ = self.client.put(f"/api/rallies/{rally.id}", json=rally.model_dump())
        resp = self.client.get(f"/api/rallies/{rally.id}")
        new_rally = rallies.RallyBaseSchema(**resp.json())
        self.assertEqual(new_rally.clip_path, rally.clip_path, msg="do not match")
        self.assertEqual(resp.status_code, 200)

        new_rally.end_frame = new_rally.start_frame - 20
        resp = self.client.put(f"/api/rallies/{new_rally.id}", json=new_rally.model_dump())
        self.assertEqual(resp.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_delete_rally(self):
        match = self.create_match()
        rally = self.create_rally(
            match=match,
            clip_path='/mnt/disk1/video1.mp4',
            start_frame=100,
            end_frame=200,
            order=1
        )

        f = self.client.delete(f"/api/rallies/{rally.id}")
        self.assertEqual(f.status_code, 200)

        r = self.client.get(f"/api/rallies/{rally.id}")
        self.assertEqual(r.status_code, 404)

    def test_get_all_rallies_check_rally_orders_in_output(self):
        # Testing rally creation and fetching for multiple rally.
        # Test rally order
        match = self.create_match()
        _ = self.create_rally(
            match=match,
            clip_path='/mnt/disk1/video1.mp4',
            start_frame=100,
            end_frame=200,
            order=0
        )

        _ = self.create_rally(
            match=match,
            clip_path='/mnt/disk1/video1.mp4',
            start_frame=500,
            end_frame=1000,
            order=2
        )

        _ = self.create_rally(
            match=match,
            clip_path='/mnt/disk1/video1.mp4',
            start_frame=250,
            end_frame=400,
            order=1
        )

        # test if the outputs come in order of occurrence in game...
        resp = self.client.get("/api/rallies/")
        js = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(js), 3)
        a, b, c = js
        self.assertTrue(a['order'] < b['order'] < c['order'])

        # check if we retrieve the sorted rallies in the matches/rallies endpoint.
        resp = self.client.get(f"/api/matches/{match.id}/rallies/")
        js = resp.json()
        a, b, c = js
        self.assertTrue(a['order'] < b['order'] < c['order'])

        resp = self.client.get(f"/api/matches/{match.id}/rallies/{a['order']}")
        rally_with_order = rallies.RallyBaseSchema(**resp.json())
        self.assertEqual(rally_with_order.start_frame, a['start_frame'])
