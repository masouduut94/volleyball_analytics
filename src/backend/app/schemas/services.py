from typing import Optional
from src.backend.app.enums.enums import ServiceType, CourtZone
from pydantic import BaseModel, Field, ConfigDict


# Shared properties
class ServiceCreateSchema(BaseModel):
    """
    serving_region: indicates the place that hitter is standing right before
        tossing the ball.
    end_frame: If we have the rally video with `rally_id`, then `end_frame` indicates the
        frame number where the model detected the endpoint of service.
    """
    model_config = ConfigDict(from_attributes=True)

    end_frame: Optional[int] = None
    end_index: Optional[int] = None
    hitter_name: Optional[str] = Field(default='Igor Kliuka', max_length=100)
    hitter_bbox: Optional[dict] = {}
    bounce_point: Optional[dict] = {}
    target_zone: Optional[int] = CourtZone.BACK_LEFT_Z1
    type: Optional[int] = ServiceType.FLOAT_SERVE
