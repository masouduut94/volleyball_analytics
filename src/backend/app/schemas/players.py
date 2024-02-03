from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# Shared properties
class PlayerCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    is_male: bool = Field(default=True)
    is_right_handed: bool = Field(default=True)
    role: Optional = Field(max_length=2)
    height: Optional[int] = Field(default=None, gt=100)
    weight: Optional[int] = Field(default=None, gt=30)
    nation_id: int = Field(default=None)
    club_id: int = Field(default=None)


class PlayerBaseSchema(PlayerCreateSchema):
    id: int = None
