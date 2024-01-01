from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml

db_file = open("../conf/db_conf.yaml").read()
cfg = yaml.load(db_file, Loader=yaml.SafeLoader)
user = cfg["postgres"]["user"]
pwd = cfg["postgres"]["password"]
host = cfg["postgres"]["host"]
db = cfg["postgres"]["db"]
port = cfg["postgres"]["port"]


SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{user}:{pwd}@{host}/{db}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
engine.connect()  # Check if it is connected

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# if psycopg-2 didn't work: sudo apt install libpq-dev gcc
