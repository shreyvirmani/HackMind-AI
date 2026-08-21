from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, Boolean
from datetime import datetime

from .connection import Base


# --------------------------------------------------------------------
# Centralized plan constants. Nothing else in the codebase should
# hardcode "free" / "pro" / "max" or the numeric generation limits --
# changing a limit later should mean editing exactly these lines.
# --------------------------------------------------------------------

PLAN_FREE = "free"
PLAN_PRO = "pro"
PLAN_MAX = "max"

PLANS = (PLAN_FREE, PLAN_PRO, PLAN_MAX)

FREE_PLAN_WEEKLY_GENERATION_LIMIT = 3
PRO_PLAN_WEEKLY_GENERATION_LIMIT = 15
MAX_PLAN_WEEKLY_GENERATION_LIMIT = None  # None == unlimited

GENERATION_WINDOW_DAYS = 7

STATUS_ACTIVE = "active"
STATUS_EXPIRED = "expired"


def generation_limit_for_plan(plan: str):
    """Single lookup used everywhere a plan's weekly generation cap
    is needed, so the free/pro/max numbers only ever live here."""

    return {
        PLAN_FREE: FREE_PLAN_WEEKLY_GENERATION_LIMIT,
        PLAN_PRO: PRO_PLAN_WEEKLY_GENERATION_LIMIT,
        PLAN_MAX: MAX_PLAN_WEEKLY_GENERATION_LIMIT,
    }.get(plan, FREE_PLAN_WEEKLY_GENERATION_LIMIT)


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

    # One of PLAN_FREE / PLAN_PRO / PLAN_MAX. Stored as a plain string
    # (not a DB-level enum), so adding a future plan tier never
    # requires a schema migration -- only a new constant above.
    plan = Column(
        String,
        nullable=False,
        default=PLAN_FREE,
    )

    status = Column(
        String,
        nullable=False,
        default=STATUS_ACTIVE,
    )

    # Generations used in the CURRENT weekly window. Free gets
    # FREE_PLAN_WEEKLY_GENERATION_LIMIT and Pro gets
    # PRO_PLAN_WEEKLY_GENERATION_LIMIT of these per rolling 7-day
    # window; Max is never capped. The window resets (count -> 0)
    # once generation_window_start is more than GENERATION_WINDOW_DAYS
    # old.
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
    a charge or a webhook is missed. Also records exactly which plan
    and duration were paid for, so payment verification never has to
    trust anything the client sends -- it re-derives the plan from
    this row alone."""

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

    # Which plan this order was created for (PLAN_PRO / PLAN_MAX).
    # Set once, server-side, at order-creation time -- verification
    # and the webhook both read it back from here rather than trusting
    # anything supplied by the client at verification time.
    plan = Column(
        String,
        nullable=False,
        default=PLAN_PRO,
    )

    months = Column(
        Integer,
        nullable=False,
        default=1,
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

    architecture = Column(
        JSON,
         nullable=True
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


class Workflow(Base):
    """
    Persisted AI-generation workflow state. This replaces the old
    in-memory WorkflowRegistry, which broke on serverless platforms
    (Vercel) because a workflow's `POST /workflow/start` call and its
    later `POST /workflow/{id}/advance` / `GET /workflow/{id}` calls
    can each land on a completely different, memory-isolated function
    instance. Every stage's status AND its output data are persisted
    here so any instance can pick up exactly where a previous one
    left off.

    Each of planner/research/architecture/judge/pitch is one of:
    "waiting" | "running" | "completed" | "failed".
    """

    __tablename__ = "workflows"

    id = Column(
        String,
        primary_key=True,
        index=True,
    )  # the workflow_id (uuid4 string)

    user_id = Column(
        String,
        nullable=False,
        index=True,
    )

    idea = Column(
        String,
        nullable=False,
    )

    planner = Column(String, nullable=False, default="waiting")
    research = Column(String, nullable=False, default="waiting")
    architecture = Column(String, nullable=False, default="waiting")
    judge = Column(String, nullable=False, default="waiting")
    pitch = Column(String, nullable=False, default="waiting")

    # Raw stage outputs (Pydantic .model_dump() dicts), persisted so
    # a later stage -- possibly running on a different instance --
    # can reconstruct the objects it depends on (e.g. architecture
    # needs the roadmap + research outputs).
    roadmap_data = Column(JSON, nullable=True)
    research_data = Column(JSON, nullable=True)
    architecture_data = Column(JSON, nullable=True)
    judge_data = Column(JSON, nullable=True)
    pitch_data = Column(JSON, nullable=True)

    finished = Column(Boolean, nullable=False, default=False)
    project_id = Column(String, nullable=True)
    error = Column(String, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )