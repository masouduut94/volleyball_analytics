from urllib.parse import urljoin
from fastapi import status
import requests as rq
from typing_extensions import List

from src.backend.app.schemas import cameras, matches, rallies, nations, players, series, teams, videos


class APIInterface:
    def __init__(self, url):
        self.base_url = url
        self.camera_url = urljoin(self.base_url, '/api/cameras/')
        self.match_url = urljoin(self.base_url, '/api/matches/')
        self.nation_url = urljoin(self.base_url, '/api/nations/')
        self.player_url = urljoin(self.base_url, '/api/players/')
        self.rally_url = urljoin(self.base_url, '/api/rallies/')
        self.series_url = urljoin(self.base_url, '/api/series/')
        self.team_url = urljoin(self.base_url, '/api/teams/')
        self.video_url = urljoin(self.base_url, '/api/videos/')
        print(f"connection status: {self.connected()}")

    def connected(self) -> bool:
        resp = rq.get(url=urljoin(self.base_url, '/api/check/'))
        return resp.status_code == status.HTTP_200_OK

    def get_camera(self, camera_id: int = None) -> cameras.CameraBaseSchema | List[cameras.CameraBaseSchema]:
        if camera_id is None:
            resp = rq.get(url=urljoin(self.camera_url, str(camera_id)))
            camera = cameras.CameraBaseSchema(**resp.json())
            return camera
        resp = rq.get(url=urljoin(self.camera_url, str(camera_id)))
        all_cameras = []
        for c in resp.json():
            camera = cameras.CameraBaseSchema(**c.json())
            all_cameras.append(camera)
        return all_cameras

    def insert_camera(self, **kwargs) -> cameras.CameraBaseSchema:
        resp = rq.post(self.camera_url, json=kwargs)
        camera = cameras.CameraBaseSchema(**resp.json())
        return camera

    def remove_camera(self, camera_id) -> bool:
        resp = rq.delete(url=urljoin(self.camera_url, str(camera_id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_video(self, video_id: int = None) -> videos.VideoBaseSchema | List[videos.VideoBaseSchema]:
        if video_id is None:
            resp = rq.get(url=urljoin(self.video_url, str(video_id)))
            video = videos.VideoBaseSchema(**resp.json())
            return video
        resp = rq.get(url=urljoin(self.video_url, str(video_id)))
        all_videos = []
        for v in resp.json():
            video = videos.VideoBaseSchema(**v.json())
            all_videos.append(video)
        return all_videos

    def insert_video(self, **kwargs) -> videos.VideoBaseSchema:
        resp = rq.post(self.video_url, json=kwargs)
        return videos.VideoBaseSchema(**resp.json())

    def remove_video(self, video_id) -> bool:
        resp = rq.delete(url=urljoin(self.video_url, str(video_id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_player(self, player_id: int = None) -> players.PlayerBaseSchema | List[players.PlayerBaseSchema]:
        if player_id is None:
            resp = rq.get(url=urljoin(self.player_url, str(player_id)))
            player = players.PlayerBaseSchema(**resp.json())
            return player
        resp = rq.get(url=urljoin(self.player_url, str(player_id)))
        all_players = []
        for p in resp.json():
            player = players.PlayerBaseSchema(**p.json())
            all_players.append(player)
        return all_players

    def insert_player(self, **kwargs) -> players.PlayerBaseSchema:
        resp = rq.post(self.player_url, json=kwargs)
        return players.PlayerBaseSchema(**resp.json())

    def remove_player(self, player_id) -> bool:
        resp = rq.delete(url=urljoin(self.player_url, str(player_id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_team(self, team_id: int = None) -> teams.TeamBaseSchema | List[teams.TeamBaseSchema]:
        if team_id is None:
            resp = rq.get(url=urljoin(self.team_url, str(team_id)))
            team = teams.TeamBaseSchema(**resp.json())
            return team
        resp = rq.get(url=urljoin(self.team_url, str(team_id)))
        all_teams = []
        for p in resp.json():
            team = teams.TeamBaseSchema(**p.json())
            all_teams.append(team)
        return all_teams

    def insert_team(self, **kwargs) -> teams.TeamBaseSchema:
        resp = rq.post(self.team_url, json=kwargs)
        return teams.TeamBaseSchema(**resp.json())

    def remove_team(self, team_id) -> bool:
        resp = rq.delete(url=urljoin(self.team_url, str(team_id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_match(self, match_id: int = None) -> matches.MatchBaseSchema | List[matches.MatchBaseSchema]:
        if match_id is None:
            resp = rq.get(url=urljoin(self.match_url, str(match_id)))
            match = matches.MatchBaseSchema(**resp.json())
            return match
        resp = rq.get(url=urljoin(self.match_url, str(match_id)))
        all_matches = []
        for p in resp.json():
            match = matches.MatchBaseSchema(**p.json())
            all_matches.append(match)
        return all_matches

    def insert_match(self, **kwargs) -> matches.MatchBaseSchema:
        resp = rq.post(self.match_url, json=kwargs)
        return matches.MatchBaseSchema(**resp.json())

    def remove_match(self, match_id) -> bool:
        resp = rq.delete(url=urljoin(self.match_url, str(match_id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_nation(self, nation_id: int = None) -> nations.NationBaseSchema | List[nations.NationBaseSchema]:
        if nation_id is None:
            resp = rq.get(url=urljoin(self.nation_url, str(nation_id)))
            nation = nations.NationBaseSchema(**resp.json())
            return nation
        resp = rq.get(url=urljoin(self.nation_url, str(nation_id)))
        all_nations = []
        for n in resp.json():
            nation = nations.NationBaseSchema(**n.json())
            all_nations.append(nation)
        return all_nations

    def insert_nation(self, **kwargs) -> nations.NationBaseSchema:
        resp = rq.post(self.nation_url, json=kwargs)
        return nations.NationBaseSchema(**resp.json())

    def remove_nation(self, nation_id) -> bool:
        resp = rq.delete(url=urljoin(self.nation_url, str(nation_id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_series(self, series_id: int = None) -> series.SeriesBaseSchema | list[series.SeriesBaseSchema]:
        if series_id is None:
            resp = rq.get(url=urljoin(self.series_url, str(series_id)))
            series_ = series.SeriesBaseSchema(**resp.json())
            return series_
        resp = rq.get(url=urljoin(self.series_url, str(series_id)))
        all_series = []
        for s in resp.json():
            series_ = series.SeriesBaseSchema(**s.json())
            all_series.append(series_)
        return all_series

    def insert_series(self, **kwargs) -> series.SeriesBaseSchema:
        resp = rq.post(self.series_url, json=kwargs)
        return series.SeriesBaseSchema(**resp.json())

    def remove_series(self, series_id) -> bool:
        resp = rq.delete(url=urljoin(self.series_url, str(series_id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_rallies(self, match_id: int = None, rally_order: int = None) -> (
            rallies.RallyBaseSchema | List[rallies.RallyBaseSchema]
    ):
        match = self.get_match(match_id)
        if match is None:
            return []

        if rally_order is None:
            url = urljoin(self.match_url, str(match_id), "rallies")
            resp = rq.get(url=url)
            rally = rallies.RallyBaseSchema(**resp.json())
            return rally

        url = urljoin(self.match_url, str(match_id), "rallies", str(rally_order))
        resp = rq.get(url=url)
        all_rallies = []
        for ra in resp.json():
            rally = rallies.RallyBaseSchema(**ra.json())
            all_rallies.append(rally)
        return all_rallies

    def get_rally_by_id(self, rally_id: int = None) -> rallies.RallyBaseSchema:
        resp = rq.get(url=urljoin(self.rally_url, str(rally_id)))
        rally = rallies.RallyBaseSchema(**resp.json())
        return rally

    def insert_rally(self, **kwargs) -> rallies.RallyBaseSchema:
        resp = rq.post(self.rally_url, json=kwargs)
        return rallies.RallyBaseSchema(**resp.json())

    def remove_rally(self, rally_id) -> bool:
        resp = rq.delete(url=urljoin(self.rally_url, str(rally_id)))
        return True if resp.status_code == status.HTTP_200_OK else False


if __name__ == '__main__':
    # uvicorn src.backend.app.app:app
    api_interface = APIInterface("http://localhost:8000")
    api_interface.connected()
