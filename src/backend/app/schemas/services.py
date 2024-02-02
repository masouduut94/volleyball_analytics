from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# Shared properties
class ServiceBaseSchema(BaseModel):
    """
    serving_region: indicates the place that hitter is standing right before
        tossing the ball.
    end_frame: If we have the rally video with `rally_id`, then `end_frame` indicates the
        frame number where the model detected the endpoint of service.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = None
    end_frame: int = Field(default=None)
    end_index: int = Field(default=None)
    hitter_name: str = Field(default='Igor Kliuka', max_length=100)
    hitter_bbox: dict = Field(default={})
    bounce_point: list = Field(default=None)
    target_zone: int = Field(default=None)
    type: int = Field(default=None)
