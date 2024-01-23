from pathlib import Path
from datetime import datetime
from schemas import TeamData, NationData, CameraData, SeriesData, RallyData, MatchData, VideoData
# from database import Base, engine
from models import *

if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Inserting teams
    t1 = TeamData(name='canada', is_national_team=True)
    t2 = TeamData(name='usa', is_national_team=True)

    team1 = Team.save(t1.model_dump())
    team2 = Team.save(t2.model_dump())

    # Inserting nations
    n1 = NationData(name='poland', display_name='POL')
    n2 = NationData(name='united states of america', display_name='USA')

    nation1 = Nation.save(n1.model_dump())
    nation2 = Nation.save(n2.model_dump())

    c1 = CameraData(angle_name='Rear_1')
    camera = Camera.save(c1.model_dump())

    se1 = SeriesData(host='gdansk', start_date=datetime.now(), end_date=datetime.now())
    se = Series.save(se1.model_dump())

    video_path = Path('/home/masoud/Desktop/projects/volleyball_analytics/data/raw/videos/train/22.mp4')
    v1 = VideoData(path=video_path.as_posix(), camera_type=camera.id)
    video = Video.save(v1.model_dump())

    m1 = MatchData(team1_id=team1.id, team2_id=team2.id, series_id=se.id, video_id=video.id)
    match1 = Match.save(m1.model_dump())

    # print(match1.to_dict())

    spikes = {
        "1": [{'x1': 12, 'x2': 1232, 'y1': 333, 'y2': 112}],
        "2": [{'x1': 12, 'x2': 1232, 'y1': 333, 'y2': 112}],
    }

    rally = RallyData(id=None, match_id=1, sets={}, spikes=spikes, blocks={}, ball_positions={}, team1_positions={},
                      team2_positions={}, rally_states="[1,2,3,4]", result={}, start_frame=30, end_frame=3330,
                      clip_path='/ewrgerag/argrawg/', service={}, receives={})

    Rally.save(rally.model_dump())

    print(rally.model_dump_json(indent=4))

    # rallies = match1.get_rallies()
    # print(rallies)
    # Inserting matches...
