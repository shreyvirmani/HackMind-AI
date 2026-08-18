"""
Tiny additive-migration helper.

This project doesn't use Alembic -- ``Base.metadata.create_all()`` in
``api/main.py`` creates any *missing tables* on startup, but it will
never add a *new column* to a table that already exists. The
free/pro/max update adds two columns to the existing ``payments``
table (``plan``, ``months``), so a plain ``create_all()`` alone would
silently leave those columns missing on any database that already has
a ``payments`` table -- i.e. every deployed environment.

``run_startup_migrations`` below adds them with
``ADD COLUMN IF NOT EXISTS`` (safe to run on every boot, on Postgres
9.6+), backfilling existing rows with sensible defaults rather than
touching or dropping anything. It does not create tables (create_all
already does that) and it never deletes data.
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.utils.logger import logger


def run_startup_migrations(engine: Engine) -> None:
    statements = [
        # Existing payment rows all predate the Pro/Max split and
        # were all for the (only, at the time) Pro plan.
        "ALTER TABLE payments ADD COLUMN IF NOT EXISTS plan VARCHAR(20) NOT NULL DEFAULT 'pro'",
        "ALTER TABLE payments ADD COLUMN IF NOT EXISTS months INTEGER NOT NULL DEFAULT 1",
    ]

    with engine.begin() as conn:
        for statement in statements:
            try:
                conn.execute(text(statement))
            except Exception as e:
                # Non-Postgres dialects (e.g. SQLite in a quick local
                # run) may not support IF NOT EXISTS the same way --
                # log and continue rather than crashing startup, since
                # create_all() already guarantees the column exists on
                # a freshly-created table either way.
                logger.warning(
                    f"Startup migration statement skipped/failed "
                    f"(likely already applied or unsupported dialect): "
                    f"{statement!r} -- {e}"
                )
