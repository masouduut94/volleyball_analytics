from typing import Optional
from pydantic import BaseModel, ConfigDict


# Shared properties
class VideoCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    camera_type_id: Optional[int] = None
    path: str


class VideoBaseSchema(VideoCreateSchema):
    id: int = None

