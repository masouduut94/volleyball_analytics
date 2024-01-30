from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session
from typing_extensions import Annotated

from src.backend.app.db import engine


def get_db() -> Session:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
