from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SeriesCreateSchema(BaseModel):
    """
    It stores the information of tournament series.
    """
    model_config = ConfigDict(from_attributes=True)

    start_date: datetime = None
    end_date: datetime = None
    host: str = Field(default=None, max_length=100)


class SeriesBaseSchema(SeriesCreateSchema):
    id: int = None
