from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
from src.backend.app.enums.enums import VolleyBallPositions as VBP


# Shared properties
class PlayerCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    is_male: bool = True
    is_right_handed: bool = True
    role: Optional[int] = VBP.OPPOSITE_HITTER
    height: Optional[int] = Field(default=None, gt=100)
    weight: Optional[int] = Field(default=None, gt=30)
    nation_id: int = None
    team_id: int = None


class PlayerBaseSchema(PlayerCreateSchema):
    id: int = None
