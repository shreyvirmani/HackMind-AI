from datetime import timedelta

from fastapi import Depends, HTTPException

from database.connection import SessionLocal
from database.repository import (
    subscription_repository,
    project_repository,
)
from database.models import (
    FREE_PLAN_WEEKLY_GENERATION_LIMIT,
    GENERATION_WINDOW_DAYS,
)

from src.auth.supabase_auth import get_current_user


class SubscriptionService:
    """
    Single source of truth for what a user's plan allows. Every
    premium-gated route depends on one of the functions below rather
    than checking `current_user` directly, so the free/pro rules live
    in exactly one place.

    Free plan: FREE_PLAN_WEEKLY_GENERATION_LIMIT generations per
    rolling GENERATION_WINDOW_DAYS-day window (resets on a rolling
    basis, not a fixed calendar day). No PDF export, no AI
    suggestions.
    Pro plan: unlimited everything, time-boxed by `expires_at`.
    """

    def get_status(self, user_id: str) -> dict:
        db = SessionLocal()
        try:
            sub = subscription_repository.get_or_create(db, user_id)
            sub = subscription_repository.expire_if_needed(db, sub)
            sub = subscription_repository.reset_window_if_needed(db, sub)

            saved_projects = len(
                project_repository.get_all_projects(db, user_id)
            )

            is_pro = sub.plan == "pro" and sub.status == "active"

            window_start = sub.generation_window_start or sub.created_at
            resets_at = (
                None
                if is_pro
                else window_start + timedelta(days=GENERATION_WINDOW_DAYS)
            )

            return {
                "plan": sub.plan,
                "status": sub.status,
                "expires_at": sub.expires_at,
                "generations_used": sub.generations_used,
                "generations_limit": (
                    None if is_pro else FREE_PLAN_WEEKLY_GENERATION_LIMIT
                ),
                "generations_period": "week",
                "resets_at": resets_at,
                "saved_projects": saved_projects,
                "is_pro": is_pro,
            }
        finally:
            db.close()

    def is_pro(self, user_id: str) -> bool:
        db = SessionLocal()
        try:
            sub = subscription_repository.get_or_create(db, user_id)
            sub = subscription_repository.expire_if_needed(db, sub)
            return sub.plan == "pro" and sub.status == "active"
        finally:
            db.close()

    def can_generate(self, user_id: str) -> bool:
        if self.is_pro(user_id):
            return True

        db = SessionLocal()
        try:
            sub = subscription_repository.get_or_create(db, user_id)
            sub = subscription_repository.reset_window_if_needed(db, sub)
            return (sub.generations_used or 0) < FREE_PLAN_WEEKLY_GENERATION_LIMIT
        finally:
            db.close()

    def record_generation(self, user_id: str) -> None:
        """Call this once a generation actually succeeds and is saved
        -- not before, so a failed/errored workflow doesn't burn a
        Free-plan generation. Pro users still get tracked (for
        visibility/analytics) but are never blocked by it."""

        db = SessionLocal()
        try:
            subscription_repository.increment_generations_used(db, user_id)
        finally:
            db.close()

    def upgrade_to_pro(self, user_id: str, months: int = 1):
        db = SessionLocal()
        try:
            return subscription_repository.upgrade_to_pro(db, user_id, months)
        finally:
            db.close()


subscription_service = SubscriptionService()


# ------------------------------------------------------------------ #
# FastAPI dependencies -- wire these into route signatures to enforce
# plan limits on the backend (never trust the frontend alone).
# ------------------------------------------------------------------ #

def require_pro(current_user=Depends(get_current_user)):
    """Use on routes that are Pro-only outright: PDF export, AI
    suggestions."""

    if not subscription_service.is_pro(current_user["id"]):
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Upgrade to Pro",
                "reason": "This feature is only available on the Pro plan.",
            },
        )

    return current_user


def require_generation_quota(current_user=Depends(get_current_user)):
    """Use on the project-generation route. Free plan gets
    FREE_PLAN_WEEKLY_GENERATION_LIMIT generations per rolling week;
    Pro is unlimited."""

    if not subscription_service.can_generate(current_user["id"]):
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Upgrade to Pro",
                "reason": (
                    f"Free plan is limited to "
                    f"{FREE_PLAN_WEEKLY_GENERATION_LIMIT} project "
                    f"generations per week. Upgrade to Pro for "
                    f"unlimited generations."
                ),
            },
        )

    return current_user