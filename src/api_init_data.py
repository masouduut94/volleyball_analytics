from datetime import datetime

from fastapi.encoders import jsonable_encoder

from src.backend.app.api_interface import APIInterface
from src.backend.app.schemas import teams, videos, series, matches, cameras

if __name__ == '__main__':
    base_url = 'http://localhost:8000'
    api = APIInterface(url=base_url)

    # insert teams
    poland_team = teams.TeamCreateSchema(name='POLAND', is_national_team=True)
    france_team = teams.TeamCreateSchema(name='FRANCE', is_national_team=True)
    poland = api.insert_team(**poland_team.model_dump())
    france = api.insert_team(**france_team.model_dump())

    # insert camera angle
    new_cam = cameras.CameraCreateSchema(angle_name='rear_camera_1')
    camera = api.insert_camera(**new_cam.model_dump())

    # insert videos
    video_path = "/home/masoud/Desktop/projects/volleyball_analytics/data/raw/videos/train/22.mp4"
    new_video = videos.VideoCreateSchema(camera_type_id=camera.id, path=video_path)
    video = api.insert_video(**new_video.model_dump())

    # Insert series
    new_tournament = series.SeriesCreateSchema(start_date=datetime.now(), end_date=datetime.now(), host='JAPAN')
    tournament = api.insert_series(**jsonable_encoder(new_tournament))

    # insert matches
    match = matches.MatchCreateSchema(
        series_id=tournament.id,
        team1_id=poland.id,
        team2_id=france.id,
        video_id=video.id
    )

    match = api.insert_match(**match.model_dump())

    print(match)
