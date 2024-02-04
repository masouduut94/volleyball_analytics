import unittest

from fastapi.encoders import jsonable_encoder as jsonify

from src.backend.app.app import app
from fastapi.testclient import TestClient
from src.backend.app.db.engine import engine, Base, get_db
from src.backend.app.schemas import teams, videos, series, players, nations, cameras, services, rallies


class UnitTestMain(unittest.TestCase):
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

    def create_nations(self, **kwargs) -> nations.NationBaseSchema:
        nation = nations.NationCreateSchema(**kwargs)
        r = self.client.post('/api/nations/', json=nation.model_dump())
        nation = nations.NationBaseSchema(**r.json())
        return nation

    def create_rallies(self, **kwargs) -> rallies.RallyBaseSchema:
        rally = rallies.RallyCreateSchema(**kwargs)
        r = self.client.post("/api/rallies/", json=rally.model_dump())
        rally = rallies.RallyBaseSchema(**r.json())
        return rally
