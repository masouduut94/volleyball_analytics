from pydantic import BaseModel, ConfigDict, Field


class CameraCreateSchema(BaseModel):
    """
    For the time being, there is only 2 camera angles and both are in the
    back of the court.
    """
    model_config = ConfigDict(from_attributes=True)

    angle_name: str = Field(max_length=20)


class CameraBaseSchema(CameraCreateSchema):
    """
    For the time being, there is only 2 camera angles and both are in the
    back of the court.
    """
    id: int = None
