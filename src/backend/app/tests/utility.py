import pendulum
import unittest

from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder as jsonify

from src.backend.app.app import app
from src.backend.app.db.engine import engine, Base, get_db
from src.backend.app.schemas import teams, videos, series, players, nations, cameras, matches, rallies


class VBTest(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        app.dependency_overrides[get_db] = get_db
        self.client = TestClient(app)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    def create_camera(self, **kwargs) -> cameras.CameraBaseSchema:
        c = cameras.CameraCreateSchema(**kwargs)
        response = self.client.post("/api/cameras/", json=c.model_dump())
        c = cameras.CameraBaseSchema(**response.json())
        return c

    def create_team(self, **kwargs) -> teams.TeamBaseSchema:
        team = teams.TeamCreateSchema(**kwargs)
        r = self.client.post('/api/teams/', json=team.model_dump())
        team = teams.TeamBaseSchema(**r.json())
        return team

    def create_series(self, **kwargs) -> series.SeriesBaseSchema:
        s = series.SeriesCreateSchema(**kwargs)
        r = self.client.post('/api/series/', json=jsonify(s))
        s = series.SeriesBaseSchema(**r.json())
        return s

    def create_players(self, **kwargs) -> players.PlayerBaseSchema:
        s = players.PlayerCreateSchema(**kwargs)
        r = self.client.post('/api/players/', json=s.model_dump())
        s = players.PlayerBaseSchema(**r.json())
        return s

    def create_video(self, **kwargs) -> videos.VideoBaseSchema:
        video = videos.VideoCreateSchema(**kwargs)
        r = self.client.post('/api/videos/', json=video.model_dump())
        video = videos.VideoBaseSchema(**r.json())
        return video

    def create_nation(self, **kwargs) -> nations.NationBaseSchema:
        nation = nations.NationCreateSchema(**kwargs)
        r = self.client.post('/api/nations/', json=nation.model_dump())
        nation = nations.NationBaseSchema(**r.json())
        return nation

    def create_rally(self, match: matches.MatchBaseSchema, **kwargs) -> rallies.RallyBaseSchema:
        rally = rallies.RallyCreateSchema(match_id=match.id, **kwargs)
        r = self.client.post("/api/rallies/", json=rally.model_dump())
        rally = rallies.RallyBaseSchema(**r.json())
        return rally

    def create_match(self):
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
        response = self.client.post("/api/matches/", json=match.model_dump())
        self.assertEqual(response.status_code, 201, msg="match creation error")
        match_output = response.json()
        match = matches.MatchBaseSchema(**match_output)
        return match
