from typing import Optional
from pydantic import BaseModel


# Shared properties
class VideoBase(BaseModel):
    camera_type: Optional[str] = None
    path: str



