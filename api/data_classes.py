import datetime
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class TeamData:
    name: str


@dataclass_json
@dataclass
class NationData:
    name: str
    display_name: str


@dataclass_json
@dataclass
class PlayerData:
    first_name: str
    last_name: str
    gender: bool
    height: int = field(default=None)
    weight: int = field(default=None)
    nation: int = field(default=None)
    club: int = field(default=None)
    age: int = field(default=None)


@dataclass_json
@dataclass
class VideoData:
    match_id: int
    path: str
    camera_type: int = field(default=0)
    type: str = field(default='main')


@dataclass_json
@dataclass
class MatchData:
    team1_id: int
    team2_id: int
    series_id: int
    video_id: int = field(default=None)


@dataclass_json
@dataclass
class RallyData:
    match_id: int
    sets: dict = field(default=None)
    spikes: dict = field(default=None)
    blocks: dict = field(default=None)
    receives: dict = field(default=None)
    serve: dict = field(default=None)
    ball_positions: dict = field(default=None)
    team1_players_positions: dict = field(default=None)
    team2_players_positions: dict = field(default=None)
    result: int = field(default=None)
    start_frame: int = field(default=None)
    end_frame: int = field(default=None)
    video_id: int = field(default=None)


@dataclass_json
@dataclass
class ServiceData:
    rally_id: int = field(default=None)
    start_frame: int = field(default=None)
    end_frame: int = field(default=None)
    video_id: int = field(default=None)
    ball_positions: dict = field(default=None)


@dataclass_json
@dataclass
class SeriesData:
    start_date: datetime = field(default=datetime.datetime.now())
    end_date: datetime = field(default=datetime.datetime.now())
    host: str = field(default=None)


@dataclass_json
@dataclass
class CameraData:
    angle_name: str


if __name__ == '__main__':
    team = TeamData(name='brazil')
    d = team.to_dict()
    print(d)
