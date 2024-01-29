import os

import sqlalchemy.orm
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

env_path = 'C:\\Users\\masoud-pc\\PycharmProjects\\volleyball_analytics\\conf\\.env'

load_dotenv(env_path)
mode = os.getenv('MODE')
if mode == 'development':
    SQLALCHEMY_DB_URL = os.getenv("DB_URL_DEVELOPMENT")
    engine = create_engine(SQLALCHEMY_DB_URL, echo=True)
    engine.connect()
else:
    SQLALCHEMY_DB_URL = os.getenv("DB_URL_TEST")
    engine = create_engine(SQLALCHEMY_DB_URL)
    engine.connect()

Session = sessionmaker(autocommit=False, autoflush=True, bind=engine)


def get_db() -> sqlalchemy.orm.Session:
    db = Session()
    try:
        yield db
    finally:
        db.close()


Base = declarative_base()
