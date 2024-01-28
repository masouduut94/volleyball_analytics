import os

import sqlalchemy.orm
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv('/home/masoud/Desktop/projects/volleyball_analytics/conf/.env')
mode = os.getenv('MODE')
SQLALCHEMY_DB_URL = os.getenv("DB_URL_DEVELOPMENT") if mode == "development" else os.getenv("DB_URL_TEST")
debug = False if mode == 'development' else True
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
