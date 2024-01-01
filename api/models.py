from datetime import datetime
from typing import List
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey

from database import Base, Session, engine


class Team(Base):
    __tablename__ = "team"

    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    name: Mapped[str] = Column(String(200), nullable=False)

    def __repr__(self):
        return f'<Team: {self.name} - id: {self.id}>'

    @classmethod
    def get(cls, id):
        session = Session()
        result = session.get(cls, id)
        return result

    @classmethod
    def get_all(cls):
        session = Session()
        result = session.query(cls).all()
        return result

    @classmethod
    def save(cls, kwargs):
        session = Session()
        new = cls(**kwargs)
        session.add(new)
        session.commit()

    @classmethod
    def update(cls, id, kwargs):
        session = Session()
        item = session.get(id)
        for k, v in kwargs.items():
            item[k] = v
        session.add(item)
        session.commit()
        session.flush()
        session.close()

    @classmethod
    def delete(cls, id):
        session = Session()
        item = session.get(cls, id)
        session.delete(item)
        session.commit()


class Nation(Base):
    __tablename__ = 'nation'
    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    name: Mapped[str] = Column(String(200))
    display_name: Mapped[str] = Column(String(200))

    def __repr__(self):
        return f"<Nation: {self.name}>"

    @classmethod
    def get(cls, id):
        session = Session()
        result = session.get(cls, id)
        return result

    @classmethod
    def get_all(cls):
        session = Session()
        result = session.query(cls).all()
        return result

    @classmethod
    def save(cls, kwargs):
        session = Session()
        new = cls(**kwargs)
        session.add(new)
        session.commit()

    @classmethod
    def update(cls, id, kwargs):
        session = Session()
        item = session.get(id)
        for k, v in kwargs.items():
            item[k] = v
        session.add(item)
        session.commit()
        session.flush()
        session.close()

    @classmethod
    def delete(cls, id):
        session = Session()
        item = session.get(cls, id)
        session.delete(item)
        session.commit()


class Player(Base):
    __tablename__ = 'player'

    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    first_name: Mapped[str] = Column(String(200))
    last_name: Mapped[str] = Column(String(200))
    gender: Mapped[bool] = Column(Boolean)
    age: Mapped[int] = Column(Integer)
    height: Mapped[int] = Column(Integer)
    weight: Mapped[int] = Column(Integer)
    nation: Mapped[int] = Column(Integer, ForeignKey("nation.id", ondelete="CASCADE"))
    club: Mapped[int] = Column(Integer, ForeignKey("team.id", ondelete="CASCADE"))

    def __repr__(self):
        return f'<Athlete: id: {self.id} - name: {self.first_name} {self.last_name} - nation: {self.nation}>'

    @classmethod
    def get(cls, id):
        session = Session()
        result = session.get(cls, id)
        return result

    @classmethod
    def get_all(cls):
        session = Session()
        result = session.query(cls).all()
        return result

    @classmethod
    def save(cls, kwargs):
        session = Session()
        new = cls(**kwargs)
        session.add(new)
        session.commit()

    @classmethod
    def update(cls, id, kwargs):
        session = Session()
        item = session.get(id)
        for k, v in kwargs.items():
            item[k] = v
        session.add(item)
        session.commit()
        session.flush()
        session.close()

    @classmethod
    def delete(cls, id):
        session = Session()
        item = session.get(cls, id)
        session.delete(item)
        session.commit()


class Source(Base):
    __tablename__ = "source"

    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    name: Mapped[str] = Column(String(200))
    match_id: Mapped["Match"] = Column(Integer, ForeignKey("match.id", ondelete="CASCADE"))
    path: Mapped[str] = Column(Text, nullable=False)

    def __repr__(self):
        return f'<Video: id: {self.id} - name: {self.first_name} {self.last_name} - path: {self.national_team}>'

    @classmethod
    def get(cls, id):
        session = Session()
        result = session.get(cls, id)
        return result

    @classmethod
    def get_all(cls):
        session = Session()
        result = session.query(cls).all()
        return result

    @classmethod
    def save(cls, kwargs):
        session = Session()
        new = cls(**kwargs)
        session.add(new)
        session.commit()

    @classmethod
    def update(cls, id, kwargs):
        session = Session()
        item = session.get(id)
        for k, v in kwargs.items():
            item[k] = v
        session.add(item)
        session.commit()
        session.flush()
        session.close()

    @classmethod
    def delete(cls, id):
        session = Session()
        item = session.get(cls, id)
        session.delete(item)
        session.commit()


class Match(Base):
    __tablename__ = 'match'

    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    # series_id: Mapped["Video"] = Column(Integer, ForeignKey("video.id"))
    team1_id: Mapped[int] = Column(Integer)
    team2_id: Mapped[int] = Column(Integer)

    rallies: Mapped[List["Rally"]] = relationship(back_populates='source_video', cascade="all, delete")

    # rallies = relationship("Rally", backref='rally', lazy='dynamic', cascade="all, delete")

    @classmethod
    def get(cls, id):
        session = Session()
        result = session.get(cls, id)
        return result

    @classmethod
    def get_all(cls):
        session = Session()
        result = session.query(cls).all()
        return result

    @classmethod
    def save(cls, kwargs):
        session = Session()
        new = cls(**kwargs)
        session.add(new)
        session.commit()

    @classmethod
    def update(cls, id, kwargs):
        session = Session()
        item = session.get(id)
        for k, v in kwargs.items():
            item[k] = v
        session.add(item)
        session.commit()
        session.flush()
        session.close()

    @classmethod
    def delete(cls, id):
        session = Session()
        item = session.get(cls, id)
        session.delete(item)
        session.commit()


class Video(Base):
    __tablename__ = "video"

    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
    source_id = Column(Integer, ForeignKey("video.id", ondelete="CASCADE"))
    # main_video = relationship("video", backref="video", lazy='dynamic', cascade="all, delete")
    path: Mapped[str] = Column(String(200), nullable=False)

    @classmethod
    def get(cls, id):
        session = Session()
        result = session.get(cls, id)
        return result

    @classmethod
    def get_all(cls):
        session = Session()
        result = session.query(cls).all()
        return result

    @classmethod
    def save(cls, kwargs):
        session = Session()
        new = cls(**kwargs)
        session.add(new)
        session.commit()

    @classmethod
    def update(cls, id, kwargs):
        session = Session()
        item = session.get(id)
        for k, v in kwargs.items():
            item[k] = v
        session.add(item)
        session.commit()
        session.flush()
        session.close()

    @classmethod
    def delete(cls, id):
        session = Session()
        item = session.get(cls, id)
        session.delete(item)
        session.commit()


class Rally(Base):
    __tablename__ = 'rally'

    id: Mapped[int] = Column(Integer, primary_key=True)
    created: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated: Mapped[datetime] = Column(DateTime, onupdate=datetime.now)
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
    result: Mapped[dict] = Column(Integer)

    source_video: Mapped["Match"] = relationship(back_populates='rallies', cascade="all, delete")

    @classmethod
    def get(cls, id):
        session = Session()
        result = session.get(cls, id)
        return result

    @classmethod
    def get_all(cls):
        session = Session()
        result = session.query(cls).all()
        return result

    @classmethod
    def save(cls, kwargs):
        session = Session()
        new = cls(**kwargs)
        session.add(new)
        session.commit()
        session.flush()
        return new

    @classmethod
    def update(cls, id, kwargs):
        session = Session()
        item = session.get(id)
        for k, v in kwargs.items():
            item[k] = v
        session.add(item)
        session.commit()
        session.flush()
        session.close()


    @classmethod
    def delete(cls, id):
        session = Session()
        item = session.get(cls, id)
        session.delete(item)
        session.commit()
        session.flush()
        session.close()


if __name__ == '__main__':
    # engine.connect()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
