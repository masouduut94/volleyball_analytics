from datetime import datetime
from typing import List
from pathlib import Path
from sqlalchemy.orm import Mapped, relationship, backref
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, ForeignKey, DateTime

from api.data_classes import TeamData, NationData, SourceData, MatchData, SeriesData
from api.database import engine, Base


class Team(Base):
    name: Mapped[str] = Column(String(200), nullable=False)
    is_national_team: Mapped[bool] = Column(Boolean, default=True)

    def __repr__(self):
        return f'<Team: {self.name} - id: {self.id}>'


class Nation(Base):
    name: Mapped[str] = Column(String(200))
    display_name: Mapped[str] = Column(String(200))

    def __repr__(self):
        return f"<Nation: {self.name}>"


class Player(Base):
    first_name: Mapped[str] = Column(String(200))
    last_name: Mapped[str] = Column(String(200))
    gender: Mapped[bool] = Column(Boolean)
    age: Mapped[int] = Column(Integer)
    height: Mapped[int] = Column(Integer)
    weight: Mapped[int] = Column(Integer)
    nation: Mapped[int] = Column(Integer, ForeignKey("nation.id", ondelete="CASCADE"))
    club: Mapped[int] = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"))

    def __repr__(self):
        return f'<Player: id: {self.id} - name: {self.first_name} {self.last_name} - nation: {self.nation}>'


class Source(Base):
    name: Mapped[str] = Column(String(200))
    path: Mapped[str] = Column(Text, nullable=False)

    def __repr__(self):
        return f'<Video: id: {self.id} - name: {self.first_name} {self.last_name} - path: {self.national_team}>'


class Series(Base):
    # series_id: Mapped["Video"] = Column(Integer, ForeignKey("video.id"))
    host: Mapped[str] = Column(String(100))
    start_date: Mapped[datetime] = Column(DateTime, default=datetime.now)
    end_date: Mapped[datetime] = Column(DateTime)

    matches: Mapped[List["Match"]] = relationship(backref='series', lazy='dynamic')


class Match(Base):
    # series_id: Mapped["Video"] = Column(Integer, ForeignKey("video.id"))
    series_id: Mapped[int] = Column(Integer, ForeignKey('series.id', ondelete="CASCADE"))
    source_id: Mapped[int] = Column(Integer, ForeignKey("source.id", ondelete="CASCADE"))

    team1_id: Mapped[int] = Column(Integer)
    team2_id: Mapped[int] = Column(Integer)

    rallies: Mapped[List["Rally"]] = relationship(back_populates='source_video')
    source: Mapped['Source'] = relationship(backref=backref("match", lazy='dynamic'))

    def get_series(self):
        s = Series.get(self.series_id)
        return s


class Video(Base):
    source_id: Mapped[int] = Column(Integer, ForeignKey("video.id", ondelete="CASCADE"))
    path: Mapped[str] = Column(String(200), nullable=False)


class Rally(Base):
    video_id: Mapped[int] = Column(Integer, ForeignKey("video.id", ondelete="CASCADE"))
    match_id: Mapped[int] = Column(Integer, ForeignKey("match.id", ondelete="CASCADE"))
    start_frame: Mapped[int] = Column(Integer)
    end_frame: Mapped[int] = Column(Integer)
    sets: Mapped[dict] = Column(JSON)
    spikes: Mapped[dict] = Column(JSON)
    blocks: Mapped[dict] = Column(JSON)
    receives: Mapped[dict] = Column(JSON)
    serve: Mapped[dict] = Column(JSON)
    ball_positions: Mapped[dict] = Column(JSON)
    team1_players_positions: Mapped[dict] = Column(JSON)
    team2_players_positions: Mapped[dict] = Column(JSON)
    result: Mapped[int] = Column(Integer)

    source_video: Mapped["Match"] = relationship(back_populates='rallies')


class Service(Base):
    rally_id: Mapped[int] = Column(Integer, ForeignKey("rally.id", ondelete="CASCADE"))
    ball_positions: Mapped[dict] = Column(JSON)
    start_frame: Mapped[int]
    end_frame: Mapped[int]
    video_path: Mapped[str]


if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Seeding initial data

    # Inserting teams
    t1 = TeamData(name='canada')
    t2 = TeamData(name='usa')

    team1 = Team.save(t1.to_dict())
    team2 = Team.save(t2.to_dict())

    # Inserting nations
    n1 = NationData(name='canada', display_name='CAN')
    n2 = NationData(name='usa', display_name='USA')

    nation1 = Nation.save(n1.to_dict())
    nation2 = Nation.save(n2.to_dict())

    video_path = Path('/media/HDD/datasets/VOLLEYBALL/RAW-VIDEOS/train/22.mp4')
    s1 = SourceData(name=video_path.stem, path=video_path.as_posix())
    src = Source.save(s1.to_dict())

    se1 = SeriesData(host='brazil', start_date=datetime.now(), end_date=datetime.now())
    se = Series.save(se1.to_dict())
    # Inserting matches...
    m1 = MatchData(team1_id=team1.id, team2_id=team2.id, series_id=se.id, source_id=src.id)
    match1 = Match.save(m1.to_dict())

    # Inserting video sources...
