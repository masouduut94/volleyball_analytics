from pydantic import BaseModel, ConfigDict


# Properties to receive on item update
class MatchCreateSchema(BaseModel):
    """
    Stores the information for a specific match.
    """
    model_config = ConfigDict(from_attributes=True)

    team1_id: int
    team2_id: int
    series_id: int
    video_id: int


class MatchBaseSchema(MatchCreateSchema):
    """
    Stores the information for a specific match.
    """
    id: int = None
