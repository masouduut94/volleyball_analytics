import pendulum

from src.backend.app.schemas import matches
from src.backend.app.tests.utility import VBTest


class MatchTest(VBTest):
    def test_post_get_match(self):
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
        # tournament = self.create_series(host='netherlands', start_date=datetime.now(), end_date=datetime.now())
        match = matches.MatchCreateSchema(
            video_id=vid.id, series_id=tournament.id, team1_id=team1.id, team2_id=team2.id
        )
        # Testing match creation and fetching for one match.
        response = self.client.post("/api/matches/", json=match.model_dump())
        self.assertEqual(response.status_code, 201)

        match_output = response.json()
        match_output = matches.MatchBaseSchema(**match_output)
        response = self.client.get(f"/api/matches/{match_output.id}")
        self.assertEqual(response.status_code, 200)

    def test_get_all_matches(self):
        # Testing match creation and fetching for multiple match.
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
        match1 = matches.MatchCreateSchema(
            video_id=vid.id, series_id=tournament.id, team1_id=team1.id, team2_id=team2.id
        )

        cam = self.create_camera(angle_name='behind_1')
        vid = self.create_video(camera_type_id=cam.id, path='22.mp4')
        team1 = self.create_team(name='iran')
        team2 = self.create_team(name='china')
        st_date = pendulum.now().subtract(months=2, weeks=4, days=3)
        end_date = pendulum.now()

        tournament = self.create_series(
            host='netherlands',
            start_date=st_date.to_iso8601_string(),
            end_date=end_date.to_iso8601_string()
        )
        match2 = matches.MatchCreateSchema(
            video_id=vid.id, series_id=tournament.id, team1_id=team1.id, team2_id=team2.id
        )

        _ = self.client.post("/api/matches/", json=match1.model_dump())
        _ = self.client.post("/api/matches/", json=match2.model_dump())

        response = self.client.get("/api/matches/")
        js = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(js), 2)

    def test_update_match(self):
        # Testing match creation and fetching for one match.
        cam = self.create_camera(angle_name='behind_1')
        vid = self.create_video(camera_type_id=cam.id, path='ss.mp4')
        team1 = self.create_team(name='usa')
        team2 = self.create_team(name='canada')
        st_date = pendulum.now().subtract(weeks=4, days=3)
        end_date = pendulum.now()

        tournament = self.create_series(
            host='netherlands',
            start_date=st_date.to_iso8601_string(),
            end_date=end_date.to_iso8601_string()
        )
        match = matches.MatchCreateSchema(
            video_id=vid.id, series_id=tournament.id, team1_id=team1.id, team2_id=team2.id
        )
        r = self.client.post("/api/matches/", json=match.model_dump())
        match = matches.MatchBaseSchema(**r.json())

        match.team2_id = team1.id
        _ = self.client.put(f"/api/matches/{match.id}", json=match.model_dump())
        r = self.client.get(f"/api/matches/{match.id}")
        output = matches.MatchBaseSchema(**r.json())
        self.assertEqual(output.team2_id, team1.id)
        self.assertEqual(r.status_code, 200)

    def test_delete_match(self):
        # Testing match creation and fetching for one match.
        cam = self.create_camera(angle_name='behind_1')
        vid = self.create_video(camera_type_id=cam.id, path='ss.mp4')
        team1 = self.create_team(name='usa')
        team2 = self.create_team(name='canada')
        st_date = pendulum.now().subtract(years=1, weeks=2, days=3)
        end_date = pendulum.now()

        tournament = self.create_series(
            host='netherlands',
            start_date=st_date.to_iso8601_string(),
            end_date=end_date.to_iso8601_string()
        )
        match = matches.MatchCreateSchema(
            video_id=vid.id, series_id=tournament.id, team1_id=team1.id, team2_id=team2.id
        )
        r = self.client.post("/api/matches/", json=match.model_dump())
        match = matches.MatchBaseSchema(**r.json())

        f = self.client.delete(f"/api/matches/{match.id}")
        self.assertEqual(f.status_code, 200)

        r = self.client.get(f"/api/matches/{match.id}")
        self.assertEqual(r.status_code, 404)
