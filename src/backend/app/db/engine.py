from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from src.backend.app.core.config import settings

engine = create_engine(settings.get_db_uri())


def get_db() -> Session:
    with Session(engine) as session:
        yield session


Base = declarative_base()
