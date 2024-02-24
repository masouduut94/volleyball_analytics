from typing_extensions import Dict, List
from pydantic import BaseModel, ConfigDict, Field  # , model_validator


class RallyCreateSchema(BaseModel):
    """
    Stores the data for each rally. all the dict-type items are
    keeping the statistics that extracted by ML pipelines.

    """
    model_config = ConfigDict(from_attributes=True)

    match_id: int
    sets: Dict[int, List] = Field(default={})
    spikes: Dict[int, List] = Field(default={})
    blocks: Dict[int, List] = Field(default={})
    receives: Dict[int, List] = Field(default={})
    ball_positions: Dict[int, List] = Field(default={})
    service: dict = Field(default={})
    team1_positions: dict = Field(default={})
    team2_positions: dict = Field(default={})
    order: int = Field(gt=-1)
    rally_states: str = Field(default="")
    result: dict = Field(default={})
    start_frame: int
    end_frame: int
    clip_path: str = Field(max_length=100)

    # @model_validator(mode='before')
    # @classmethod
    # def check_date(cls, data: Any) -> Any:
    #     if isinstance(data, dict):
    #         if data['start_frame'] >= data['end_frame']:
    #             raise ValueError("The start_frame must be less than end_frame...")
    #     return data

    # @model_validator(mode='after')
    # @classmethod
    # def check_start_date(cls, data: Any) -> Any:
    #     if isinstance(data, dict):
    #         if data['start_frame'] >= data['end_frame']:
    #             raise ValueError("The start_frame must be less than end_frame...")
    #     return data


class RallyBaseSchema(RallyCreateSchema):
    id: int = None
