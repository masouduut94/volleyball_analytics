from pydantic import BaseModel, ConfigDict, Field


class CameraBaseSchema(BaseModel):
    """
    For the time being, there is only 2 camera angles and both are in the
    back of the court.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = None
    angle_name: str = Field(max_length=20)
