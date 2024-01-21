"""
These dataclasses are utilized to help us for the SQL ORM objects serialization for JSON input and outputs.

"""
import datetime
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin


@dataclass
class TeamData(DataClassJsonMixin):
    """
    Stores the data about national and club teams.
    """
    name: str
    is_national_team: bool

    @classmethod
    def from_instance(cls, instance):
        inst_dict = instance.to_dict()
        new = cls(**inst_dict)
        return new


@dataclass
class NationData(DataClassJsonMixin):
    """
    Stores the nationalities and how they are displayed on the scoreboard.
    """
    name: str
    display_name: str

    @classmethod
    def from_instance(cls, instance):
        inst_dict = instance.to_dict()
        new = cls(**inst_dict)
        return new

@dataclass
class PlayerData(DataClassJsonMixin):
    """
    Basic information about the players.
    """
    first_name: str
    last_name: str
    gender: bool
    height: int = field(default=None)
    weight: int = field(default=None)
    nation: int = field(default=None)
    club: int = field(default=None)
    birthdate: datetime.datetime = field(default=None)

    @classmethod
    def from_instance(cls, instance):
        inst_dict = instance.to_dict()
        new = cls(**inst_dict)
        return new


@dataclass
class VideoData(DataClassJsonMixin):
    """
    information about videos stored on database.
    type: Video types can be either main or rally. `rally`-type indicates that
        video is clipped for a specific rally that belongs to some match.
        `main-type` indicates the video for specific game.
    """
    match_id: int
    path: str
    camera_type: int = field(default=0)
    type: str = field(default='main')

    @classmethod
    def from_instance(cls, instance):
        inst_dict = instance.to_dict()
        new = cls(**inst_dict)
        return new


@dataclass
class MatchData(DataClassJsonMixin):
    """
    Stores the information for a specific match.
    """
    team1_id: int
    team2_id: int
    series_id: int
    video_id: int = field(default=None)

    @classmethod
    def from_instance(cls, instance):
        inst_dict = instance.to_dict()
        new = cls(**inst_dict)
        return new


@dataclass
class RallyData(DataClassJsonMixin):
    """
    Stores the data for each rally. all the dict-type items are
    keeping the statistics that extracted by ML pipelines.

    """
    match_id: int
    sets: dict = field(default=None)
    spikes: dict = field(default=None)
    blocks: dict = field(default=None)
    receives: dict = field(default=None)
    service: dict = field(default=None)
    ball_positions: dict = field(default=None)
    team1_positions: dict = field(default=None)
    team2_positions: dict = field(default=None)
    rally_states: str = field(default=None)
    result: int = field(default=None)
    start_frame: int = field(default=None)
    end_frame: int = field(default=None)
    video_id: int = field(default=None)

    @classmethod
    def from_instance(cls, instance):
        inst_dict = instance.to_dict()
        new = cls(**inst_dict)
        return new


@dataclass
class ServiceData(DataClassJsonMixin):
    """
    serving_region: indicates the place that hitter is standing right before
        tossing the ball.
    end_frame: If we have the rally video with `rally_id`, then `end_frame` indicates the
        frame number where the model detected the endpoint of service.

    """
    end_frame: int = field(default=None)
    end_index: int = field(default=None)
    hitter: str = field(default=None)
    serving_region: dict = field(default=None)
    bounce_point: list = field(default=None)
    target_zone:  int = field(default=None)
    type: int = field(default=None)


@dataclass
class SeriesData(DataClassJsonMixin):
    """
    It stores the information of tournament series.
    """
    start_date: datetime = field(default=datetime.datetime.now())
    end_date: datetime = field(default=datetime.datetime.now())
    host: str = field(default=None)

    @classmethod
    def from_instance(cls, instance):
        inst_dict = instance.to_dict()
        new = cls(**inst_dict)
        return new


@dataclass
class CameraData(DataClassJsonMixin):
    """
    For the time being, there is only 2 camera angles and both are in the
    back of the court.
    """
    angle_name: str

    @classmethod
    def from_instance(cls, instance):
        inst_dict = instance.to_dict()
        new = cls(**inst_dict)
        return new


if __name__ == '__main__':
    team = TeamData(name='brazil', is_national_team=True)
    d = team.to_dict()
    print(d)
