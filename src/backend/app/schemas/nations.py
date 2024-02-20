from pydantic import BaseModel, Field, ConfigDict


# Shared properties


class NationCreateSchema(BaseModel):
    """
    Stores the nationalities and how they are displayed on the scoreboard.
    """
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(max_length=60)
    display_name: str = Field(max_length=10)


class NationBaseSchema(NationCreateSchema):
    """
    Stores the nationalities and how they are displayed on the scoreboard.
    """
    id: int = None
