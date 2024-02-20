from pydantic import BaseModel, ConfigDict


# Shared properties
class TeamCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = None
    is_national_team: bool = True


class TeamBaseSchema(TeamCreateSchema):
    id: int = None
