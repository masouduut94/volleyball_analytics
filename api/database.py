import os

import sqlalchemy.orm
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

load_dotenv('/home/masoud/Desktop/projects/volleyball_analytics/conf/.env')
mode = os.getenv('MODE')
if mode == 'development':
    SQLALCHEMY_DB_URL = os.getenv("DB_URL_DEVELOPMENT")
    engine = create_engine(SQLALCHEMY_DB_URL)
    engine.connect()
else:
    SQLALCHEMY_DB_URL = os.getenv("DB_URL_TEST")
    engine = create_engine(
        SQLALCHEMY_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    engine.connect()

Session = sessionmaker(autocommit=False, autoflush=True, bind=engine)


def get_db() -> sqlalchemy.orm.Session:
    db = Session()
    try:
        yield db
    finally:
        db.close()


Base = declarative_base()
