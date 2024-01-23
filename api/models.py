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
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, ForeignKey, DateTime, ForeignKeyConstraint
# from sqlalchemy.dialects.postgresql
from api.database import Base, engine


class Team(Base):
    name: Mapped[str] = Column(String(200), nullable=False)
    is_national_team: Mapped[bool] = Column(Boolean, default=True)


class Nation(Base):
    name: Mapped[str] = Column(String(200))
    display_name: Mapped[str] = Column(String(200))


class Player(Base):
    first_name: Mapped[str] = Column(String(200))
    last_name: Mapped[str] = Column(String(200))
    gender: Mapped[bool] = Column(Boolean)
    role: Mapped[str] = Column(String)
    age: Mapped[int] = Column(Integer)
    height: Mapped[int] = Column(Integer)
    weight: Mapped[int] = Column(Integer)
    nation_id: Mapped[int] = Column(Integer, ForeignKey("nation.id", ondelete="CASCADE"))
    team_id: Mapped[int] = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"))

    ForeignKeyConstraint(["team_id"], ["team.id"], name="fk_element_player_team_id")
    ForeignKeyConstraint(["nation_id"], ["nation.id"], name="fk_element_player_nation_id")

    def get_team(self):
        return Team.get(self.team_id)

    def get_nation(self):
        return Nation.get(self.nation_id)


class Series(Base):
    host: Mapped[str] = Column(String(100))
    start_date: Mapped[datetime] = Column(DateTime, default=datetime.now)
    end_date: Mapped[datetime] = Column(DateTime)

    def matches(self):
        return Match.query().filter(Match.series_id == self.id).all()


class Camera(Base):
    angle_name: Mapped[str] = Column(String(100))


class Match(Base):
    # series_id: Mapped["Video"] = Column(Integer, ForeignKey("video.id"))
    series_id: Mapped[int] = Column(Integer, ForeignKey('series.id', ondelete="CASCADE"))
    video_id: Mapped[int] = Column(Integer, ForeignKey("video.id", ondelete="CASCADE"))
    team1_id: Mapped[int] = Column(Integer)
    team2_id: Mapped[int] = Column(Integer)

    rallies: Mapped[List["Rally"]] = relationship('Rally', lazy='joined', primaryjoin="Match.id == Rally.match_id")

    ForeignKeyConstraint(["series_id"], ["series.id"], name="fk_element_series_id")
    ForeignKeyConstraint(["video_id"], ["video.id"], name="fk_element_video_id")

    def team1(self):
        return Team.get(self.team1_id)

    def team2(self):
        return Team.get(self.team2_id)

    def series(self):
        return Series.get(self.series_id)

    def get_rallies(self):
        return Rally.query().filter(Rally.match_id == self.id).all()

    def video(self):
        return Video.get(self.video_id)


class Video(Base):
    camera_type: Mapped[int] = Column(Integer, ForeignKey('camera.id'))
    path: Mapped[str] = Column(String(200), nullable=False)


class Rally(Base):
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

    ForeignKeyConstraint(["match_id"], ["match.id"], name="fk_element_match_id")

    def get_match(self):
        return Match.get(self.match_id).one()
