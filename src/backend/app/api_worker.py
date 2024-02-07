from os.path import join
from fastapi import status
import requests as rq
from typing_extensions import List

from src.backend.app.schemas import cameras, matches, rallies, nations, players, series, teams, videos


class APIInterface:
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

    def remove_camera(self, id) -> bool:
        resp = rq.delete(url=join(self.camera_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_video(self, id: int = None) -> videos.VideoBaseSchema | List[videos.VideoBaseSchema]:
        if id is None:
            resp = rq.get(url=join(self.video_url, str(id)))
            video = videos.VideoBaseSchema(**resp.json())
            return video
        resp = rq.get(url=join(self.video_url, str(id)))
        all_videos = []
        for v in resp.json():
            video = videos.VideoBaseSchema(**v.json())
            all_videos.append(video)
        return all_videos

    def insert_video(self, **kwargs) -> videos.VideoBaseSchema:
        resp = rq.post(self.video_url, json=kwargs)
        return videos.VideoBaseSchema(**resp.json())

    def remove_video(self, id) -> bool:
        resp = rq.delete(url=join(self.video_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_player(self, id: int = None) -> players.PlayerBaseSchema | List[players.PlayerBaseSchema]:
        if id is None:
            resp = rq.get(url=join(self.player_url, str(id)))
            player = players.PlayerBaseSchema(**resp.json())
            return player
        resp = rq.get(url=join(self.player_url, str(id)))
        all_players = []
        for p in resp.json():
            player = players.PlayerBaseSchema(**p.json())
            all_players.append(player)
        return all_players

    def insert_player(self, **kwargs) -> players.PlayerBaseSchema:
        resp = rq.post(self.player_url, json=kwargs)
        return players.PlayerBaseSchema(**resp.json())

    def remove_player(self, id) -> bool:
        resp = rq.delete(url=join(self.player_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_team(self, id: int = None) -> teams.TeamBaseSchema | List[teams.TeamBaseSchema]:
        if id is None:
            resp = rq.get(url=join(self.team_url, str(id)))
            team = teams.TeamBaseSchema(**resp.json())
            return team
        resp = rq.get(url=join(self.team_url, str(id)))
        all_teams = []
        for p in resp.json():
            team = teams.TeamBaseSchema(**p.json())
            all_teams.append(team)
        return all_teams

    def insert_team(self, **kwargs) -> teams.TeamBaseSchema:
        resp = rq.post(self.team_url, json=kwargs)
        return teams.TeamBaseSchema(**resp.json())

    def remove_team(self, id) -> bool:
        resp = rq.delete(url=join(self.team_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_match(self, id: int = None) -> matches.MatchBaseSchema | List[matches.MatchBaseSchema]:
        if id is None:
            resp = rq.get(url=join(self.match_url, str(id)))
            match = matches.MatchBaseSchema(**resp.json())
            return match
        resp = rq.get(url=join(self.match_url, str(id)))
        all_matches = []
        for p in resp.json():
            match = matches.MatchBaseSchema(**p.json())
            all_matches.append(match)
        return all_matches

    def insert_match(self, **kwargs) -> matches.MatchBaseSchema:
        resp = rq.post(self.match_url, json=kwargs)
        return matches.MatchBaseSchema(**resp.json())

    def remove_match(self, id) -> bool:
        resp = rq.delete(url=join(self.match_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_nation(self, id: int = None) -> nations.NationBaseSchema | List[nations.NationBaseSchema]:
        if id is None:
            resp = rq.get(url=join(self.nation_url, str(id)))
            nation = nations.NationBaseSchema(**resp.json())
            return nation
        resp = rq.get(url=join(self.nation_url, str(id)))
        all_nations = []
        for n in resp.json():
            nation = nations.NationBaseSchema(**n.json())
            all_nations.append(nation)
        return all_nations

    def insert_nation(self, **kwargs) -> nations.NationBaseSchema:
        resp = rq.post(self.nation_url, json=kwargs)
        return nations.NationBaseSchema(**resp.json())

    def remove_nation(self) -> bool:
        resp = rq.delete(url=join(self.nation_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_series(self, id: int = None) -> series.SeriesBaseSchema | list[series.SeriesBaseSchema]:
        if id is None:
            resp = rq.get(url=join(self.series_url, str(id)))
            series_ = series.SeriesBaseSchema(**resp.json())
            return series_
        resp = rq.get(url=join(self.series_url, str(id)))
        all_series = []
        for s in resp.json():
            series_ = series.SeriesBaseSchema(**s.json())
            all_series.append(series_)
        return all_series

    def insert_series(self, **kwargs) -> series.SeriesBaseSchema:
        resp = rq.post(self.series_url, json=kwargs)
        return series.SeriesBaseSchema(**resp.json())

    def remove_series(self, id) -> bool:
        resp = rq.delete(url=join(self.series_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_rallies(self, match_id: int = None, rally_order: int = None) -> (
            rallies.RallyBaseSchema | List[rallies.RallyBaseSchema]
    ):
        match = self.get_match(match_id)
        if match is None:
            return []

        if rally_order is None:
            url = join(self.match_url, str(match_id), "rallies")
            resp = rq.get(url=url)
            rally = rallies.RallyBaseSchema(**resp.json())
            return rally

        url = join(self.match_url, str(match_id), "rallies", str(rally_order))
        resp = rq.get(url=url)
        all_rallies = []
        for ra in resp.json():
            rally = rallies.RallyBaseSchema(**ra.json())
            all_rallies.append(rally)
        return all_rallies

    def get_rally_by_id(self, rally_id: int = None) -> rallies.RallyBaseSchema:
        resp = rq.get(url=join(self.rally_url, str(rally_id)))
        rally = rallies.RallyBaseSchema(**resp.json())
        return rally

    def insert_rally(self, **kwargs) -> rallies.RallyBaseSchema:
        resp = rq.post(self.rally_url, json=kwargs)
        return rallies.RallyBaseSchema(**resp.json())

    def remove_rally(self, id) -> bool:
        resp = rq.delete(url=join(self.rally_url, str(id)))
        return True if resp.status_code == status.HTTP_200_OK else False
