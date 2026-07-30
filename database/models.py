from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from datetime import datetime

from .connection import Base


FREE_PLAN_WEEKLY_GENERATION_LIMIT = 3
GENERATION_WINDOW_DAYS = 7


class Subscription(Base):

    __tablename__ = "subscriptions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    plan = Column(
        String,
        nullable=False,
        default="free",
    )

    status = Column(
        String,
        nullable=False,
        default="active",
    )

    # Generations used in the CURRENT weekly window. Free plan gets
    # FREE_PLAN_WEEKLY_GENERATION_LIMIT of these per rolling 7-day
    # window; the window resets (count -> 0) once
    # generation_window_start is more than GENERATION_WINDOW_DAYS old.
    generations_used = Column(
        Integer,
        nullable=False,
        default=0,
    )

    generation_window_start = Column(
        DateTime,
        default=datetime.utcnow,
    )

    expires_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class Payment(Base):
    """Audit trail of Razorpay orders/payments, for support &
    reconciliation. Not required for enforcement (Subscription is the
    source of truth for access), but invaluable when a user disputes
    a charge or a webhook is missed."""

    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        String,
        nullable=False,
        index=True,
    )

    razorpay_order_id = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    razorpay_payment_id = Column(
        String,
        nullable=True,
    )

    amount = Column(
        Integer,  # smallest currency unit (paise for INR)
        nullable=False,
    )

    currency = Column(
        String,
        nullable=False,
        default="INR",
    )

    status = Column(
        String,
        nullable=False,
        default="created",  # created | paid | failed
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


class Project(Base):

    __tablename__ = "projects"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        String,
        nullable=False,
        index=True,
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