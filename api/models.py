"""
This is the core ORM objects to interact with DB.
Note that you need to initialize the Postgres/Mysql tables before running this script.

$ sudo -i -u postgres
$ psql
$ CREATE DATABASE volleyball;
or
$ DROP DATABASE volleyball;
$ CREATE DATABASE volleyball;

relationships in SQLALCHEMY ORM
https://vegibit.com/sqlalchemy-orm-relationships-one-to-many-many-to-one-many-to-many/

"""
from datetime import datetime
from typing_extensions import List, Dict, Any
from sqlalchemy.orm import Mapped, relationship, declared_attr
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, ForeignKey, DateTime, ForeignKeyConstraint
# from sqlalchemy.dialects.postgresql
from api.database import Base, get_db


class Team(Base):
    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    name: Mapped[str] = Column(String(200), nullable=False)
    is_national_team: Mapped[bool] = Column(Boolean, default=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Nation(Base):
    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    name: Mapped[str] = Column(String(200))
    display_name: Mapped[str] = Column(String(200))

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Player(Base):
    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    first_name: Mapped[str] = Column(String(200))
    last_name: Mapped[str] = Column(String(200))
    gender: Mapped[bool] = Column(Boolean)
    role: Mapped[str] = Column(String)
    age: Mapped[int] = Column(Integer)
    height: Mapped[int] = Column(Integer)
    weight: Mapped[int] = Column(Integer)
    nation_id: Mapped[int] = Column(Integer, ForeignKey("nation.id", ondelete="CASCADE"))
    team_id: Mapped[int] = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"))

    ForeignKeyConstraint(("team_id",), ["team.id"], name="fk_element_player_team_id")
    ForeignKeyConstraint(("nation_id",), ["nation.id"], name="fk_element_player_nation_id")

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def get_team(self):
        db = get_db()
        return db.get(Team, self.team_id).one()

    def get_nation(self):
        db = get_db()
        return db.get(Nation, self.nation_id).one()


class Series(Base):
    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    host: Mapped[str] = Column(String(100))
    start_date: Mapped[datetime] = Column(DateTime, default=datetime.now)
    end_date: Mapped[datetime] = Column(DateTime)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def matches(self):
        db = get_db()
        return db.query(Match).filter(Match.series_id == self.id).all()


class Camera(Base):
    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    angle_name: Mapped[str] = Column(String(100))

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Match(Base):
    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    series_id: Mapped[int] = Column(Integer, ForeignKey('series.id', ondelete="CASCADE"))
    video_id: Mapped[int] = Column(Integer, ForeignKey("video.id", ondelete="CASCADE"))
    team1_id: Mapped[int] = Column(Integer)
    team2_id: Mapped[int] = Column(Integer)

    rallies: Mapped[List["Rally"]] = relationship('Rally', lazy='joined', primaryjoin="Match.id == Rally.match_id")

    ForeignKeyConstraint(("series_id",), ["series.id"], name="fk_element_series_id")
    ForeignKeyConstraint(("video_id",), ["video.id"], name="fk_element_video_id")

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def team1(self):
        db = get_db()
        return db.get(Team, self.team1_id).one()

    def team2(self):
        db = get_db()
        return db.get(Team, self.team2_id).one()

    def series(self):
        db = get_db()
        return db.get(Series, self.series_id).one()

    def get_rallies(self):
        db = get_db()
        return db.query(Rally).filter(Rally.match_id == self.id).all()

    def video(self):
        db = get_db()
        return db.get(Video, self.video_id).one()


class Video(Base):
    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    camera_type: Mapped[int] = Column(Integer, ForeignKey('camera.id'))
    path: Mapped[str] = Column(String(200), nullable=False)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Rally(Base):
    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    match_id: Mapped[int] = Column(Integer, ForeignKey('match.id', ondelete="CASCADE"))
    clip_path: Mapped[str] = Column(String(200))
    start_frame: Mapped[int] = Column(Integer)
    end_frame: Mapped[int] = Column(Integer)
    sets: Mapped[dict] = Column(JSON)
    spikes: Mapped[dict] = Column(JSON)
    blocks: Mapped[dict] = Column(JSON)
    receives: Mapped[dict] = Column(JSON)
    service: Mapped[dict] = Column(JSON)
    ball_positions: Mapped[dict] = Column(JSON)
    rally_states: Mapped[str] = Column(Text)
    team1_positions: Mapped[dict] = Column(JSON)
    team2_positions: Mapped[dict] = Column(JSON)
    result: Mapped[dict] = Column(JSON)

    ForeignKeyConstraint(("match_id",), ["match.id"], name="fk_element_match_id")

    def get_match(self):
        db = get_db()
        return db.get(Match, self.match_id).one()

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


