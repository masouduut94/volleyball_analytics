"""
This is the core ORM objects to interact with DB.
Note that you need to initialize the Postgres/Mysql tables before running this script.

$ sudo -i -u postgres
$ psql
$ CREATE DATABASE volleyball;
or
$ DROP DATABASE volleyball;
$ CREATE DATABASE volleyball;

"""
from typing import List
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, ForeignKey, DateTime, ForeignKeyConstraint

from api.database import engine, Base
from api.data_classes import TeamData, NationData, VideoData, MatchData, SeriesData, CameraData


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
    age: Mapped[int] = Column(Integer)
    height: Mapped[int] = Column(Integer)
    weight: Mapped[int] = Column(Integer)
    nation_id: Mapped[int] = Column(Integer, ForeignKey("nation.id", ondelete="CASCADE"))
    team_id: Mapped[int] = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"))
    ForeignKeyConstraint(["team_id"], ["team.id"], name="fk_element_player_team_id")
    ForeignKeyConstraint(["nation_id"], ["nation.id"], name="fk_element_player_nation_id")


class Series(Base):
    # series_id: Mapped["Video"] = Column(Integer, ForeignKey("video.id"))
    host: Mapped[str] = Column(String(100))
    start_date: Mapped[datetime] = Column(DateTime, default=datetime.now)
    end_date: Mapped[datetime] = Column(DateTime)

    matches: Mapped[List["Match"]] = relationship(backref='series', lazy='dynamic')


class Camera(Base):
    angle_name: Mapped[str] = Column(String(100))


class Match(Base):
    # series_id: Mapped["Video"] = Column(Integer, ForeignKey("video.id"))
    series_id: Mapped[int] = Column(Integer, ForeignKey('series.id', ondelete="CASCADE"))
    video_id: Mapped[int] = Column(Integer, ForeignKey("video.id", ondelete="CASCADE"))
    team1_id: Mapped[int] = Column(Integer)
    team2_id: Mapped[int] = Column(Integer)

    ForeignKeyConstraint(["series_id"], ["series.id"], name="fk_element_series_id")
    ForeignKeyConstraint(["video_id"], ["video.id"], name="fk_element_video_id")

    def get_series(self):
        s = Series.get(self.series_id)
        return s

    def get_rallies(self):
        results = Rally.query().filter(Rally.match_id == self.id).all()
        return results

    @staticmethod
    def get_main_video(video_id):
        return Video.query().filter(Video.id == video_id and type == "main").one()


class Video(Base):
    camera_type: Mapped[int] = Column(Integer, ForeignKey('camera.id'))
    path: Mapped[str] = Column(String(200), nullable=False)
    type: Mapped[str] = Column(String(50), nullable=False)  # 3 types: main, rally, serve

    # ForeignKeyConstraint(["match_id"], ["match.id"], name="fk_element_match_id")

    def get_videos_by_type(self, video_type='main'):
        return self.query().filter(self.type == video_type).one()


class Rally(Base):
    match_id: Mapped[int] = Column(Integer, ForeignKey("match.id", ondelete="CASCADE"))
    video_id: Mapped[int] = Column(Integer, ForeignKey("video.id", ondelete="CASCADE"))
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
    result: Mapped[int] = Column(Integer)

    video: Mapped["Video"] = relationship(backref="video")
    ForeignKeyConstraint(["match_id"], ["match.id"], name="fk_element_match_id")
    ForeignKeyConstraint(["video_id"], ["video.id"], name="fk_element_video_id")


if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Inserting teams
    t1 = TeamData(name='canada', is_national_team=True)
    t2 = TeamData(name='usa', is_national_team=True)

    team1 = Team.save(t1.to_dict())
    team2 = Team.save(t2.to_dict())
    print(team1)
    print(team2)

    # Inserting nations
    n1 = NationData(name='canada', display_name='CAN')
    n2 = NationData(name='usa', display_name='USA')

    nation1 = Nation.save(n1.to_dict())
    nation2 = Nation.save(n2.to_dict())

    c1 = CameraData(angle_name='behind_1')
    camera = Camera.save(c1.to_dict())

    se1 = SeriesData(host='brazil', start_date=datetime.now(), end_date=datetime.now())
    se = Series.save(se1.to_dict())

    m1 = MatchData(team1_id=team1.id, team2_id=team2.id, series_id=se.id, video_id=None)
    match1 = Match.save(m1.to_dict())

    video_path = Path('/home/masoud/Desktop/projects/volleyball_analytics/data/raw/videos/train/22.mp4')
    v1 = VideoData(path=video_path.as_posix(), camera_type=camera.id, type='main')
    video = Video.save(v1.to_dict())

    match1.update({"video_id": video.id})
    # Inserting matches...
