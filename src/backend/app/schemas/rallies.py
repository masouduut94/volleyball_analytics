from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Dict, List

from src.backend.app.schemas.services import ServiceCreateSchema


# Shared properties
class RallyCreateSchema(BaseModel):
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
    service: dict = ServiceCreateSchema
    ball_positions: Dict[int, Dict[str, List[int | float]]] = Field(default={})
    team1_positions: dict = Field(default={})
    team2_positions: dict = Field(default={})
    rally_states: str = Field(default="")
    result: dict = Field(default={})
    start_frame: int
    end_frame: int
    clip_path: str = Field(max_length=100)


class RallyBaseSchema(RallyCreateSchema):
    id: int = None



