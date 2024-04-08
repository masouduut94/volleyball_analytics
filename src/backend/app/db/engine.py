from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from loguru import logger
import sys
from src.backend.app.core.config import settings

logger.add(sink=sys.stderr, format="{time:MMMM D, YYYY > HH:mm:ss!UTC} | {level} | {message}", serialize=True)
db_uri = settings.get_db_uri()
mode = settings.MODE
engine = create_engine(db_uri)
logger.info(f"The `MODE` is {mode} ")
msg = f"The db = {settings.DEV_DB if mode != 'test' else settings.TEST_DB_URL} is selected."
logger.success(msg)


def get_db() -> Session:
    with Session(engine) as session:
        yield session


Base = declarative_base()
