from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from src.backend.app.core.config import settings

engine = create_engine(settings.get_db_uri())
Base = declarative_base()
