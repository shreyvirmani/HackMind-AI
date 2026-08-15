"""
One-off manual Pro upgrade for a specific user_id.

Usage:
    python scripts/manual_upgrade.py <user_id> [months]

Example:
    python scripts/manual_upgrade.py 948927ac-f86a-4aef-9402-be46424bc579 1

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


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/manual_upgrade.py <user_id> [months]")
        sys.exit(1)

    user_id = sys.argv[1]
    months = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    db = SessionLocal()
    try:
        sub = subscription_repository.upgrade_to_pro(db, user_id, months=months)

        print("Upgraded successfully:")
        print(f"  user_id:    {sub.user_id}")
        print(f"  plan:       {sub.plan}")
        print(f"  status:     {sub.status}")
        print(f"  expires_at: {sub.expires_at}")
    finally:
        db.close()


if __name__ == "__main__":
    main()