import requests as rq
from os.path import join
from fastapi import status
from urllib.parse import urljoin
from typing_extensions import List

from src.backend.app.schemas import cameras, matches, rallies, nations, players, series, teams, videos


class APIInterface:
    """It helps to interact with the API."""
    def __init__(self, url):
        """

        Args:
            url(str):
        """
        self.base_url = url
        self.camera_url = urljoin(self.base_url, '/api/cameras/')
        self.match_url = urljoin(self.base_url, '/api/matches/')
        self.nation_url = urljoin(self.base_url, '/api/nations/')
        self.player_url = urljoin(self.base_url, '/api/players/')
        self.rally_url = urljoin(self.base_url, '/api/rallies/')
        self.series_url = urljoin(self.base_url, '/api/series/')
        self.team_url = urljoin(self.base_url, '/api/teams/')
        self.video_url = urljoin(self.base_url, '/api/videos/')
        try:
            rq.get(url=urljoin(self.base_url, '/api/check/'), timeout=0.001)
        except ConnectionError:
            print("Connection Failure. make sure API is up! ")
        else:
            print("API connection established.")

    def get_camera(self, camera_id: int = None) -> cameras.CameraBaseSchema | List[cameras.CameraBaseSchema]:
        if camera_id is not None:
            resp = rq.get(url=urljoin(self.camera_url, str(camera_id)))
            camera = cameras.CameraBaseSchema(**resp.json())
            return camera
        resp = rq.get(url=self.camera_url)
        all_cameras = []
        for c in resp.json():
            camera = cameras.CameraBaseSchema(**c)
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
        if video_id is not None:
            resp = rq.get(url=urljoin(self.video_url, str(video_id)))
            video = videos.VideoBaseSchema(**resp.json())
            return video
        resp = rq.get(self.video_url)
        all_videos = []
        for v in resp.json():
            video = videos.VideoBaseSchema(**v)
            all_videos.append(video)
        return all_videos

    def insert_video(self, **kwargs) -> videos.VideoBaseSchema:
        resp = rq.post(self.video_url, json=kwargs)
        return videos.VideoBaseSchema(**resp.json())

    def remove_video(self, video_id) -> bool:
        resp = rq.delete(url=urljoin(self.video_url, str(video_id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_player(self, player_id: int = None) -> players.PlayerBaseSchema | List[players.PlayerBaseSchema]:
        if player_id is not None:
            resp = rq.get(url=urljoin(self.player_url, str(player_id)))
            player = players.PlayerBaseSchema(**resp.json())
            return player
        resp = rq.get(self.player_url)
        all_players = []
        for p in resp.json():
            player = players.PlayerBaseSchema(**p)
            all_players.append(player)
        return all_players

    def insert_player(self, **kwargs) -> players.PlayerBaseSchema:
        resp = rq.post(self.player_url, json=kwargs)
        return players.PlayerBaseSchema(**resp.json())

    def remove_player(self, player_id) -> bool:
        resp = rq.delete(url=urljoin(self.player_url, str(player_id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_team(self, team_id: int = None) -> teams.TeamBaseSchema | List[teams.TeamBaseSchema]:
        if team_id is not None:
            resp = rq.get(url=urljoin(self.team_url, str(team_id)))
            team = teams.TeamBaseSchema(**resp.json())
            return team
        resp = rq.get(url=self.team_url)
        all_teams = []
        for p in resp.json():
            team = teams.TeamBaseSchema(**p)
            all_teams.append(team)
        return all_teams

    def insert_team(self, **kwargs) -> teams.TeamBaseSchema:
        resp = rq.post(self.team_url, json=kwargs)
        return teams.TeamBaseSchema(**resp.json())

    def remove_team(self, team_id) -> bool:
        resp = rq.delete(url=urljoin(self.team_url, str(team_id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_match(self, match_id: int = None) -> matches.MatchBaseSchema | List[matches.MatchBaseSchema]:
        if match_id is not None:
            resp = rq.get(url=urljoin(self.match_url, str(match_id)))
            match = matches.MatchBaseSchema(**resp.json())
            return match
        resp = rq.get(url=self.match_url)
        all_matches = []
        for m in resp.json():
            match = matches.MatchBaseSchema(**m)
            all_matches.append(match)
        return all_matches

    def insert_match(self, **kwargs) -> matches.MatchBaseSchema:
        resp = rq.post(self.match_url, json=kwargs)
        return matches.MatchBaseSchema(**resp.json())

    def remove_match(self, match_id) -> bool:
        resp = rq.delete(url=urljoin(self.match_url, str(match_id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_nation(self, nation_id: int = None) -> nations.NationBaseSchema | List[nations.NationBaseSchema]:
        if nation_id is not None:
            resp = rq.get(url=urljoin(self.nation_url, str(nation_id)))
            nation = nations.NationBaseSchema(**resp.json())
            return nation
        resp = rq.get(url=self.nation_url)
        all_nations = []
        for n in resp.json():
            nation = nations.NationBaseSchema(**n)
            all_nations.append(nation)
        return all_nations

    def insert_nation(self, **kwargs) -> nations.NationBaseSchema:
        resp = rq.post(self.nation_url, json=kwargs)
        return nations.NationBaseSchema(**resp.json())

    def remove_nation(self, nation_id) -> bool:
        resp = rq.delete(url=urljoin(self.nation_url, str(nation_id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_series(self, series_id: int = None) -> series.SeriesBaseSchema | list[series.SeriesBaseSchema]:
        if series_id is not None:
            resp = rq.get(url=urljoin(self.series_url, str(series_id)))
            series_ = series.SeriesBaseSchema(**resp.json())
            return series_
        resp = rq.get(url=self.series_url)
        all_series = []
        for s in resp.json():
            series_ = series.SeriesBaseSchema(**s)
            all_series.append(series_)
        return all_series

    def insert_series(self, **kwargs) -> series.SeriesBaseSchema:
        resp = rq.post(self.series_url, json=kwargs)
        return series.SeriesBaseSchema(**resp.json())

    def remove_series(self, series_id) -> bool:
        resp = rq.delete(url=urljoin(self.series_url, str(series_id)))
        return True if resp.status_code == status.HTTP_200_OK else False

    def get_rallies(self, match_id: int = None, rally_order: int = None) -> \
            rallies.RallyBaseSchema | List[rallies.RallyBaseSchema]:
        match = self.get_match(match_id)
        if match is None:
            return []
        suffix = join(str(match_id), "rallies")
        url = urljoin(self.match_url, suffix)

        if rally_order is None:
            resp = rq.get(url=url)
            all_rallies = []
            for ra in resp.json():
                rally = rallies.RallyBaseSchema(**ra)
                all_rallies.append(rally)
            return all_rallies

        suffix = join(suffix, str(rally_order))
        url = urljoin(self.match_url, suffix)
        resp = rq.get(url=url)
        rally = rallies.RallyBaseSchema(**resp.json())
        return rally

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

    def rally_update(self, rally: rallies.RallyBaseSchema):
        url = urljoin(self.rally_url, str(rally.id))
        resp = rq.put(url, json=rally.model_dump(exclude={'id'}))
        return True if resp.status_code == status.HTTP_202_ACCEPTED else False


if __name__ == '__main__':
    # uvicorn src.backend.app.app:app
    api = APIInterface("http://localhost:8000")
    # p = api.get_rallies(match_id=1)
    t = api.get_rallies(match_id=1, rally_order=2)
