"""
Pydantic implementation of the data_classes...

model_computed_fields: a dictionary of the computed fields of this model instance.
model_construct(): a class method for creating models without running validation. See Creating models without validation.
model_copy(): returns a copy (by default, shallow copy) of the model. See Serialization.
model_dump(): returns a dictionary of the model's fields and values. See Serialization.
model_dump_json(): returns a JSON string representation of model_dump(). See Serialization.
model_extra: get extra fields set during validation.
model_fields_set: set of fields which were set when the model instance was initialized.
model_json_schema(): returns a jsonable dictionary representing the model as JSON Schema. See JSON Schema.
model_parametrized_name(): compute the class name for parametrization of generic classes.
model_post_init(): perform additional initialization after the model is initialized.
model_rebuild(): rebuild the model schema, which also supports building recursive generic models. See Rebuild model schema.
model_validate(): a utility for loading any object into a model. See Helper functions.
model_validate_json(): a utility for validating the given JSON data against the Pydantic

"""
from datetime import datetime
# from typing_extensions import ClassVar
from typing_extensions import Dict, List, Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints, Field


class TeamData(BaseModel):
    """
    Stores the data about national and club teams.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = None
    name: str = Field(max_length=60)
    is_national_team: bool = Field(default=True)


class NationData(BaseModel):
    """
    Stores the nationalities and how they are displayed on the scoreboard.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = None
    name: str = Field(max_length=60)
    display_name: str = Field(max_length=10)


class PlayerData(BaseModel):
    """
    Basic information about the players.
    """
    model_config = ConfigDict(from_attributes=True)

    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    is_male: bool = Field(default=True)
    role: str = Field(max_length=2)
    height: int = Field(default=None, gt=100)
    weight: int = Field(default=None, gt=30)
    nation: int = Field(default=None)
    club: int = Field(default=None)
    birthdate: datetime = Field(default_factory=datetime.now)


class VideoData(BaseModel):
    """
    information about videos stored on database.
    type: Video types can be either main or rally. `rally`-type indicates that
        video is clipped for a specific rally that belongs to some match.
        `main-type` indicates the video for specific game.
    """
    model_config = ConfigDict(from_attributes=True)

    path: str = Field(max_length=100)
    camera_type: int = Field(default=None)


class MatchData(BaseModel):
    """
    Stores the information for a specific match.
    """
    model_config = ConfigDict(from_attributes=True)

    team1_id: int
    team2_id: int
    series_id: int
    video_id: int

    # rallies: ClassVar[int] = []


class ServiceData(BaseModel):
    """
    serving_region: indicates the place that hitter is standing right before
        tossing the ball.
    end_frame: If we have the rally video with `rally_id`, then `end_frame` indicates the
        frame number where the model detected the endpoint of service.

    """
    end_frame: int = Field(default=None)
    end_index: int = Field(default=None)
    hitter_name: str = Field(default='Igor Kliuka', max_length=100)
    hitter_bbox: dict = Field(default={})
    bounce_point: list = Field(default=None)
    target_zone: int = Field(default=None)
    type: int = Field(default=None)


class RallyData(BaseModel):
    """
    Stores the data for each rally. all the dict-type items are
    keeping the statistics that extracted by ML pipelines.

    """
    model_config = ConfigDict(from_attributes=True)

    match_id: int
    sets: Dict[int, List[Dict[str, int | float]]] = Field(default={})
    spikes: Dict[int, List[Dict[str, int | float]]] = Field(default={})
    blocks: Dict[int, List[Dict[str, int | float]]] = Field(default={})
    receives: Dict[int, List[Dict[str, int | float]]] = Field(default={})
    service: dict = ServiceData
    ball_positions: Dict[int, Dict[str, List[int | float]]] = Field(default={})
    team1_positions: dict = Field(default={})
    team2_positions: dict = Field(default={})
    rally_states: str = Field(default="")
    result: dict = Field(default={})
    start_frame: int
    end_frame: int
    clip_path: str = Field(max_length=100)

    # match: ClassVar[int] = []


class SeriesData(BaseModel):
    """
    It stores the information of tournament series.
    """
    start_date: datetime = Field(default_factory=datetime.now)
    end_date: datetime = Field(default_factory=datetime.now)
    host: str = Field(default=None, max_length=100)


class CameraData(BaseModel):
    """
    For the time being, there is only 2 camera angles and both are in the
    back of the court.
    """
    angle_name: str = Field(max_length=20)


if __name__ == '__main__':
    team = TeamData(name='brazil', is_national_team=True)
    d = team.model_dump()
    print(d)
