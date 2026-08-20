from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool, NullPool

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
# Vercel automatically sets the VERCEL env var on every deployed
# function, so this is a reliable way to tell serverless apart from
# Railway's single long-lived process without needing a separate
# config flag.
#
# On Railway, one process serves many requests over its lifetime, so
# an in-process QueuePool (reused connections) is the right call --
# unchanged from before.
#
# On Vercel, each invocation may run in a fresh, short-lived
# instance. A QueuePool sized for a long-lived server (10 + 20
# overflow = up to 30 connections) gets created fresh on every cold
# start; under real concurrent traffic this can open far more total
# Postgres connections than Supabase allows, since nothing recycles
# a pool that only ever lives for one invocation. NullPool opens
# exactly one connection per request and closes it immediately after
# -- correct for this model, and it's what lets Supabase's own
# PgBouncer (transaction-mode pooler, port 6543) do the actual
# pooling instead. See DEPLOYMENT.md for the DATABASE_URL Vercel
# should use.

IS_SERVERLESS = os.getenv("VERCEL") is not None

if IS_SERVERLESS:

    engine = create_engine(
        DATABASE_URL,

        poolclass=NullPool,

        pool_pre_ping=True,

        pool_reset_on_return="rollback",

        echo=False,

        future=True,
    )

else:

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