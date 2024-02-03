from typing import Optional

from pydantic import BaseModel, ConfigDict


# Shared properties
class TeamBaseCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = None
    is_national_team: bool = True


class TeamBaseSchema(TeamBaseCreateSchema):
    id: int = None
