import datetime

from dataclasses_json import dataclass_json
from dataclasses import dataclass


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
    age: int
    height: int
    weight: int
    nation: int
    club: int


@dataclass_json
@dataclass
class SourceData:
    name: str
    match_id: int
    path: str


@dataclass_json
@dataclass
class MatchData:
    team1_id: int
    team2_id: int


@dataclass_json
@dataclass
class VideoData:
    source_id: int
    # main_video = relationship("video", backref="video", lazy='dynamic', cascade="all, delete")
    path: str


@dataclass_json
@dataclass
class RallyData:
    video_id: int
    match_id: int
    start_frame: int
    end_frame: int
    sets: dict
    spikes: dict
    blocks: dict
    receives: dict
    serve: dict
    ball_positions: dict
    team1_players_positions: dict
    team2_players_positions: dict
    result: int


@dataclass_json
@dataclass
class ServiceData:
    rally_id: int
    ball_positions: dict
    start_frame: int
    end_frame: int
    video_path: str


if __name__ == '__main__':
    team = TeamData(name='brazil')
    d = team.to_dict()
    print(d)
