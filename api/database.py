import yaml
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, DateTime, inspect
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, declared_attr

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
Session = sessionmaker(autocommit=False, autoflush=True, bind=engine)


class ModelMixin(object):
    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __repr__(self):
        attrs = {
            c.key: c.value for c in inspect(self).attrs
        }
        id_value = attrs.pop('id')
        t = ''
        for key, value in attrs.items():
            t += f"{key}: {value} | "
        return f'<{self.__class__.__name__} | id: {id_value} | {t}'

    @classmethod
    def get(cls, id):
        session = Session()
        result = session.get(cls, id)
        session.close()
        return result

    @classmethod
    def get_all(cls):
        session = Session()
        result = session.query(cls).all()
        session.close()
        return result

    def query(self):
        session = Session()
        result = session.query(self)
        return result

    @classmethod
    def save(cls, kwargs):
        session = Session()
        new = cls(**kwargs)
        session.add(new)
        session.commit()
        session.refresh(new)
        session.close()
        return new

    @classmethod
    def update(cls, id, kwargs):
        session = Session()
        item = cls.get(id)
        for k, v in kwargs.items():
            setattr(item, k, v)
        session.add(item)
        session.commit()
        session.flush()
        session.close()

    @classmethod
    def delete(cls, id):
        session = Session()
        item = cls.get(id)
        session.delete(item)
        session.commit()
        session.close()


Base = declarative_base(cls=ModelMixin)

# if psycopg-2 didn't work: sudo apt install libpq-dev gcc
