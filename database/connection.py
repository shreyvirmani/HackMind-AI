from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool

from dotenv import load_dotenv

import os

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is missing."
    )

# --------------------------------------------------
# SQLAlchemy Engine
# --------------------------------------------------

engine = create_engine(
    DATABASE_URL,

    # Verify connections before using them
    pool_pre_ping=True,

    # Recycle idle connections every 5 minutes
    pool_recycle=300,

    # Connection Pool Settings
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,

    # Rollback unfinished transactions automatically
    pool_reset_on_return="rollback",

    # Helpful for debugging if needed
    echo=False,

    future=True,
)

# --------------------------------------------------
# Session Factory
# --------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# --------------------------------------------------
# Base Model
# --------------------------------------------------

Base = declarative_base()

# --------------------------------------------------
# Dependency
# --------------------------------------------------

def get_db():
    db = SessionLocal()

    try:
        yield db

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()