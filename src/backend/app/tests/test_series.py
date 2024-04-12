from datetime import datetime
import pendulum

from fastapi import status
from fastapi.encoders import jsonable_encoder as jsonify
from src.backend.app.schemas import series, matches
from src.backend.app.tests.utility import VBTest


class SeriesTest(VBTest):

    def test_get_one_series(self):
        # Testing series creation and fetching for one series.
        st_date = pendulum.now().subtract(weeks=2, days=3)
        end_date = pendulum.now()

        s = series.SeriesCreateSchema(
            start_date=st_date.to_iso8601_string(),
            end_date=end_date.to_iso8601_string(),
            host='Europe - Finland'
        )

        response = self.client.post("/api/series/", json=jsonify(s))
        self.assertEqual(response.status_code, 201)

        series_output = response.json()
        series_output = series.SeriesBaseSchema(**series_output)
        response = self.client.get(f"/api/series/{series_output.id}")
        self.assertEqual(response.status_code, 200)

    def test_update_series(self):
        # Testing series creation and fetching for one series.
        st_date = pendulum.now().subtract(weeks=2, days=3)
        end_date = pendulum.now()

        t = series.SeriesCreateSchema(
            start_date=st_date.to_iso8601_string(),
            end_date=end_date.to_iso8601_string(),
            host='Europe - Finland'
        )
        r = self.client.post("/api/series/", json=jsonify(t))
        t = series.SeriesBaseSchema(**r.json())

        t.host = 'SENEGAL'
        _ = self.client.put(f"/api/series/{t.id}", json=jsonify(t))
        r = self.client.get(f"/api/series/{t.id}")
        output = r.json()
        output = series.SeriesBaseSchema(**output)
        self.assertEqual(output.host, t.host)
        self.assertEqual(r.status_code, 200)

    def test_delete_series(self):
        # Testing series creation and fetching for one series.
        st_date = pendulum.now().subtract(weeks=2, days=3)
        end_date = pendulum.now()

        t = series.SeriesCreateSchema(
            start_date=st_date.to_iso8601_string(),
            end_date=end_date.to_iso8601_string(),
            host='Europe - Finland'
        )
        r = self.client.post("/api/series/", json=jsonify(t))
        t = series.SeriesBaseSchema(**r.json())

        f = self.client.delete(f"/api/series/{t.id}")
        self.assertEqual(f.status_code, 200)

        r = self.client.get(f"/api/series/{t.id}")
        self.assertEqual(r.status_code, 404)

    def test_get_all_series(self):
        # Testing series creation and fetching for multiple series.
        st_date = pendulum.now().subtract(weeks=2, days=3)
        end_date = pendulum.now()

        st_date2 = pendulum.now().subtract(weeks=5, days=3)
        end_date2 = pendulum.now().add(years=1)

        t = series.SeriesCreateSchema(
            start_date=st_date.to_iso8601_string(),
            end_date=end_date.to_iso8601_string(),
            host='Europe - Finland'
        )
        e = series.SeriesCreateSchema(
            start_date=st_date2.to_iso8601_string(),
            end_date=end_date2.to_iso8601_string(),
            host='Europe - Finland'
        )
        response = self.client.post("/api/series/", json=jsonify(t))
        response = self.client.post("/api/series/", json=jsonify(e))

        response = self.client.get("/api/series/")
        js = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(js), 2)

    def test_get_matches(self):
        cam1 = self.create_camera(angle_name='behind_1')
        cam2 = self.create_camera(angle_name='behind_2')

        vid1 = self.create_video(camera_type_id=cam1.id, path='ss.mp4')
        vid2 = self.create_video(camera_type_id=cam2.id, path='ff.mp4')

        team1 = self.create_team(name='usa')
        team2 = self.create_team(name='canada')
        team3 = self.create_team(name='iran')
        team4 = self.create_team(name='bulgaria')

        tournament = self.create_series(host='netherlands', start_date=datetime.now(), end_date=datetime.now())
        match1 = matches.MatchCreateSchema(
            video_id=vid1.id, series_id=tournament.id, team1_id=team1.id, team2_id=team2.id
        )
        match2 = matches.MatchCreateSchema(
            video_id=vid2.id, series_id=tournament.id, team1_id=team3.id, team2_id=team4.id
        )
        resp1 = self.client.post("/api/matches/", json=match1.model_dump())
        resp2 = self.client.post("/api/matches/", json=match2.model_dump())

        self.assertTrue(resp1.status_code == resp2.status_code == status.HTTP_201_CREATED)

        resp3 = self.client.get(f"/api/series/{tournament.id}/matches")
        self.assertEqual(resp3.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp3.json()), 2)
        self.assertIn(resp1.json()['id'], [item['id'] for item in resp3.json()])
        self.assertIn(resp2.json()['id'], [item['id'] for item in resp3.json()])
