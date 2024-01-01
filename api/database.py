from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml

db_file = open("/home/masoud/Desktop/projects/volleyball_analytics/conf/db_conf.yaml").read()
cfg = yaml.load(db_file, Loader=yaml.SafeLoader)
# db_type = 'mysql'
db_type = 'postgres'

user = cfg[db_type]["user"]
pwd = cfg[db_type]["password"]
host = cfg[db_type]["host"]
db = cfg[db_type]["db"]
port = cfg[db_type]["port"]
dialect = cfg[db_type]["dialect"]
driver = cfg[db_type]["driver"]


SQLALCHEMY_DB_URL = f'{dialect}+{driver}://{user}:{pwd}@{host}:{port}/{db}'

engine = create_engine(SQLALCHEMY_DB_URL)
engine.connect()  # Check if it is connected

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# if psycopg-2 didn't work: sudo apt install libpq-dev gcc
