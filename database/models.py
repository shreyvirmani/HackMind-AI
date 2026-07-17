from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from datetime import datetime

from .connection import Base


class Project(Base):

    __tablename__ = "projects"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    project_title = Column(
        String,
        nullable=False
    )

    idea = Column(
        String,
        nullable=False
    )

    roadmap = Column(
        JSON,
        nullable=False
    )

    research = Column(
        JSON,
        nullable=False
    )

    judge = Column(
        JSON,
        nullable=False
    )

    pitch_deck = Column(
        JSON,
        nullable=False
    )

    overall_score = Column(
        Float,
        default=0
    )

    status = Column(
        String,
        default="completed"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )