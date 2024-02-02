from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# Shared properties
class NationBaseSchema(BaseModel):
    """
    Stores the nationalities and how they are displayed on the scoreboard.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = None
    name: str = Field(max_length=60)
    display_name: str = Field(max_length=10)