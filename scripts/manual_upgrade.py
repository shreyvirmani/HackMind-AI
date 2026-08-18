"""
One-off manual plan upgrade for a specific user_id.

Usage:
    python scripts/manual_upgrade.py <user_id> [plan] [months]

plan defaults to "pro" if omitted, for backwards compatibility with
the original Pro-only version of this script. Valid values: pro, max.

Examples:
    python scripts/manual_upgrade.py 948927ac-f86a-4aef-9402-be46424bc579
    python scripts/manual_upgrade.py 948927ac-f86a-4aef-9402-be46424bc579 max
    python scripts/manual_upgrade.py 948927ac-f86a-4aef-9402-be46424bc579 pro 3

On Railway, run this against your deployed database with:
    railway run python scripts/manual_upgrade.py 948927ac-f86a-4aef-9402-be46424bc579
"""

import sys
import os

# Make sure the repo root (parent of this scripts/ folder) is on the
# import path -- running `python scripts\manual_upgrade.py` directly
# on Windows does NOT add the repo root to sys.path automatically,
# only the scripts/ folder itself, which is why `database`/`src`
# imports fail without this.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import SessionLocal
from database.repository import subscription_repository
from database.models import PLAN_PRO, PLAN_MAX


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/manual_upgrade.py <user_id> [plan] [months]")
        sys.exit(1)

    user_id = sys.argv[1]
    plan = sys.argv[2] if len(sys.argv) > 2 else PLAN_PRO
    months = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    if plan not in (PLAN_PRO, PLAN_MAX):
        print(f"Invalid plan {plan!r} -- must be 'pro' or 'max'.")
        sys.exit(1)

    db = SessionLocal()
    try:
        sub = subscription_repository.upgrade_plan(db, user_id, plan, months=months)

        print("Upgraded successfully:")
        print(f"  user_id:    {sub.user_id}")
        print(f"  plan:       {sub.plan}")
        print(f"  status:     {sub.status}")
        print(f"  expires_at: {sub.expires_at}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
