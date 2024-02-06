from os.path import join
from fastapi import status
import requests as rq
from typing_extensions import List

from src.backend.app.schemas import cameras, matches, rallies, nations, players, series, teams, videos


class APIHandler:
    def __init__(self, url):
        self.base_url = url
        self.camera_url = join(self.base_url, '/api/cameras/')
        self.match_url = join(self.base_url, '/api/matches/')
        self.nation_url = join(self.base_url, '/api/nations/')
        self.player_url = join(self.base_url, '/api/players/')
        self.rally_url = join(self.base_url, '/api/rallies/')
        self.series_url = join(self.base_url, '/api/series/')
        self.team_url = join(self.base_url, '/api/teams/')
        self.video_url = join(self.base_url, '/api/videos/')

        print(f"connection status: {self._connected()}")

    def _connected(self) -> bool:
        resp = rq.get(url=join(self.base_url, '/api/check'))
        return resp.status_code == status.HTTP_200_OK

    def get_camera(self, id: int = None) -> cameras.CameraBaseSchema | List[cameras.CameraBaseSchema]:
        if id is None:
            resp = rq.get(url=join(self.camera_url, str(id)))
            camera = cameras.CameraBaseSchema(**resp.json())
            return camera
        resp = rq.get(url=join(self.camera_url, str(id)))
        all_cameras = []
        for c in resp.json():
            camera = cameras.CameraBaseSchema(**c.json())
            all_cameras.append(camera)
        return all_cameras

    def insert_camera(self, **kwargs) -> cameras.CameraBaseSchema:
        resp = rq.post(self.camera_url, json=kwargs)
        camera = cameras.CameraBaseSchema(**resp.json())
        return camera

    def remove_camera(self, id):
        resp = rq.delete(url=join(self.camera_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_video(self, id: int = None):
        pass

    def insert_video(self, **kwargs):
        resp = rq.post(self.video_url, json=kwargs)
        return videos.VideoBaseSchema(**resp.json())

    def remove_video(self, id):
        resp = rq.delete(url=join(self.video_url, str(id)))
        return resp

    def get_player(self, id: int = None):
        pass

    def insert_player(self, **kwargs):
        resp = rq.post(self.player_url, json=kwargs)
        return players.PlayerBaseSchema(**resp.json())

    def remove_player(self, id):
        resp = rq.delete(url=join(self.player_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_team(self, id: int = None):
        pass

    def insert_team(self, **kwargs):
        resp = rq.post(self.team_url, json=kwargs)
        return teams.TeamBaseSchema(**resp.json())

    def remove_team(self, id):
        resp = rq.delete(url=join(self.team_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_match(self, id: int = None):
        pass

    def insert_match(self, **kwargs):
        resp = rq.post(self.match_url, json=kwargs)
        return matches.MatchBaseSchema(**resp.json())

    def remove_match(self, id):
        resp = rq.delete(url=join(self.match_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_nation(self, id: int = None):
        pass

    def insert_nation(self, **kwargs):
        resp = rq.post(self.nation_url, json=kwargs)
        return nations.NationBaseSchema(**resp.json())

    def remove_nation(self):
        resp = rq.delete(url=join(self.nation_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_series(self, id: int = None):
        pass

    def insert_series(self, **kwargs):
        resp = rq.post(self.series_url, json=kwargs)
        return series.SeriesBaseSchema(**resp.json())

    def remove_series(self, id):
        resp = rq.delete(url=join(self.series_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_rallies(self, id: int = None):
        pass

    def insert_rally(self, **kwargs):
        resp = rq.post(self.rally_url, json=kwargs)
        return rallies.RallyBaseSchema(**resp.json())

    def remove_rally(self, id):
        resp = rq.delete(url=join(self.rally_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False
