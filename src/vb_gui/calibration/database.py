from pathlib import Path
from datetime import datetime

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    DateTime,
    Text,
    Boolean,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
)
import json


# -----------------------------
# SQLAlchemy Base
# -----------------------------
class Base(DeclarativeBase):
    pass


# -----------------------------
# ORM Model for Calibrations
# -----------------------------
class CalibrationRecord(Base):
    __tablename__ = "calibrations"

    id: Mapped[int] = mapped_column(primary_key=True)

    video_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    frame_index: Mapped[int] = mapped_column(Integer, nullable=False)

    annotation_json: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


# -----------------------------
# ORM Model for Court Models
# -----------------------------
class CourtModel(Base):
    __tablename__ = "court_models"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    path: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)

    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


# -----------------------------
# Database Interface
# -----------------------------
class CalibrationDB:
    def __init__(self, db_path: str = "volleyball_calibration.db"):
        self.db_path = Path(db_path)

        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=False,
            future=True,
        )

        Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    # -------------------------
    # Calibration Records
    # -------------------------

    def load(self, video_name: str):
        with self.Session() as session:
            record = (
                session.query(CalibrationRecord)
                .filter_by(video_name=video_name)
                .first()
            )

            if record is None:
                return None

            return json.loads(record.annotation_json)

    def save(self, video_name: str, data: dict):
        with self.Session() as session:

            record = (
                session.query(CalibrationRecord)
                .filter_by(video_name=video_name)
                .first()
            )

            annotation_json = json.dumps(data)

            if record is None:
                record = CalibrationRecord(
                    video_name=video_name,
                    frame_index=data.get("frame_index", 0),
                    annotation_json=annotation_json,
                )
                session.add(record)

            else:
                record.frame_index = data.get("frame_index", 0)
                record.annotation_json = annotation_json

            session.commit()

    def exists(self, video_name: str) -> bool:
        with self.Session() as session:
            return (
                    session.query(CalibrationRecord)
                    .filter_by(video_name=video_name)
                    .first()
                    is not None
            )

    def delete(self, video_name: str):
        with self.Session() as session:
            record = (
                session.query(CalibrationRecord)
                .filter_by(video_name=video_name)
                .first()
            )

            if record:
                session.delete(record)
                session.commit()

    def list_videos(self):
        with self.Session() as session:
            records = (
                session.query(CalibrationRecord)
                .order_by(CalibrationRecord.updated_at.desc())
                .all()
            )

            return [r.video_name for r in records]

    def rename(self, old_name: str, new_name: str):
        with self.Session() as session:

            record = (
                session.query(CalibrationRecord)
                .filter_by(video_name=old_name)
                .first()
            )

            if record is None:
                raise ValueError(f"Video '{old_name}' not found.")

            if self.exists(new_name):
                raise ValueError(f"Video '{new_name}' already exists.")

            record.video_name = new_name
            session.commit()

    # -------------------------
    # Court Models Management
    # -------------------------

    def get_court_models(self):
        """Get all court detection models."""
        with self.Session() as session:
            models = session.query(CourtModel).order_by(CourtModel.name).all()

            return [
                {
                    'id': m.id,
                    'name': m.name,
                    'path': m.path,
                    'is_default': m.is_default
                }
                for m in models
            ]

    def get_default_court_model(self):
        """Get the default court detection model."""
        with self.Session() as session:
            model = session.query(CourtModel).filter_by(is_default=True).first()

            if model:
                return {
                    'id': model.id,
                    'name': model.name,
                    'path': model.path,
                    'is_default': model.is_default
                }
            return None

    def add_court_model(self, name, path):
        """Add a new court detection model."""
        with self.Session() as session:
            # Check if model already exists
            existing = session.query(CourtModel).filter_by(path=path).first()
            if existing:
                return False

            # If no default model exists, make this the default
            default_exists = session.query(CourtModel).filter_by(is_default=True).first()

            model = CourtModel(
                name=name,
                path=path,
                is_default=not default_exists  # Make default if no default exists
            )

            session.add(model)
            session.commit()
            return True

    def set_default_court_model(self, model_id):
        """Set a model as the default court detection model."""
        with self.Session() as session:
            # Clear any existing default
            session.query(CourtModel).filter_by(is_default=True).update({"is_default": False})

            # Set the new default
            model = session.query(CourtModel).filter_by(id=model_id).first()
            if not model:
                return False

            model.is_default = True
            session.commit()
            return True

    def delete_court_model(self, model_id):
        """Delete a court detection model."""
        with self.Session() as session:
            model = session.query(CourtModel).filter_by(id=model_id).first()
            if not model:
                return False

            # Check if this is the default model
            was_default = model.is_default

            session.delete(model)

            # If deleted model was default, set the first available as default
            if was_default:
                remaining = session.query(CourtModel).first()
                if remaining:
                    remaining.is_default = True

            session.commit()
            return True

    def get_court_model_by_path(self, path):
        """Get a court model by its path."""
        with self.Session() as session:
            model = session.query(CourtModel).filter_by(path=path).first()

            if model:
                return {
                    'id': model.id,
                    'name': model.name,
                    'path': model.path,
                    'is_default': model.is_default
                }
            return None