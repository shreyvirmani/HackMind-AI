from datetime import timedelta

from fastapi import Depends, HTTPException

from database.connection import SessionLocal
from database.repository import (
    subscription_repository,
    project_repository,
)
from database.models import (
    PLAN_PRO,
    PLAN_MAX,
    STATUS_ACTIVE,
    FREE_PLAN_WEEKLY_GENERATION_LIMIT,
    PRO_PLAN_WEEKLY_GENERATION_LIMIT,
    GENERATION_WINDOW_DAYS,
    generation_limit_for_plan,
)

from src.auth.supabase_auth import get_current_user
from src.utils.logger import logger


class SubscriptionService:
    """
    Single source of truth for what a user's plan allows. Every
    premium-gated route depends on one of the functions below rather
    than checking `current_user` directly, so the free/pro/max rules
    live in exactly one place.

    Free plan: FREE_PLAN_WEEKLY_GENERATION_LIMIT generations per
    rolling GENERATION_WINDOW_DAYS-day window (resets on a rolling
    basis, not a fixed calendar day). No premium features.
    Pro plan: PRO_PLAN_WEEKLY_GENERATION_LIMIT generations per rolling
    window, plus every premium feature. Time-boxed by `expires_at`.
    Max plan: unlimited generations, plus every premium feature.
    Time-boxed by `expires_at`.

    "Premium" (Idea Generator, Architecture Agent, PDF export, LLM
    Prompt Generator, AI Suggestions, project editing) means Pro OR
    Max -- `is_pro()` below intentionally returns True for Max too,
    since every route currently gated with `require_pro` is meant to
    be unlocked by *either* paid tier. Max-exclusive behavior (never
    being blocked by the generation quota) is handled separately in
    `can_generate()`.
    """

    # ------------------------------------------------------------ #
    # Plan lookup
    # ------------------------------------------------------------ #

    def _get_active_subscription(self, db, user_id: str):
        sub = subscription_repository.get_or_create(db, user_id)
        sub = subscription_repository.expire_if_needed(db, sub)
        return sub

    def get_plan(self, user_id: str) -> str:
        """Returns the user's current plan, having already applied
        expiry (an expired Pro/Max subscription reports as 'free')."""

        db = SessionLocal()
        try:
            sub = self._get_active_subscription(db, user_id)
            return sub.plan
        finally:
            db.close()

    def is_pro(self, user_id: str) -> bool:
        """True for an active Pro OR Max subscription. Use this (via
        `require_pro`) to gate any feature available on both paid
        tiers -- which, per the current plan matrix, is every premium
        feature except unlimited generations."""

        db = SessionLocal()
        try:
            sub = self._get_active_subscription(db, user_id)
            return sub.plan in (PLAN_PRO, PLAN_MAX) and sub.status == STATUS_ACTIVE
        finally:
            db.close()

    def is_max(self, user_id: str) -> bool:
        """True only for an active Max subscription."""

        db = SessionLocal()
        try:
            sub = self._get_active_subscription(db, user_id)
            return sub.plan == PLAN_MAX and sub.status == STATUS_ACTIVE
        finally:
            db.close()

    # ------------------------------------------------------------ #
    # Generation quota
    # ------------------------------------------------------------ #

    def can_generate(self, user_id: str) -> bool:
        db = SessionLocal()
        try:
            sub = self._get_active_subscription(db, user_id)

            if sub.plan == PLAN_MAX:
                return True

            sub = subscription_repository.reset_window_if_needed(db, sub)
            limit = generation_limit_for_plan(sub.plan)

            return (sub.generations_used or 0) < limit
        finally:
            db.close()

    def record_generation(self, user_id: str) -> None:
        """Call this once a generation actually succeeds and is saved
        -- not before, so a failed/errored workflow doesn't burn a
        generation. Max users still get tracked (for visibility/
        analytics) but are never blocked by it."""

        db = SessionLocal()
        try:
            subscription_repository.increment_generations_used(db, user_id)
        finally:
            db.close()

    # ------------------------------------------------------------ #
    # Status payload for the frontend
    # ------------------------------------------------------------ #

    def get_status(self, user_id: str) -> dict:
        db = SessionLocal()
        try:
            sub = self._get_active_subscription(db, user_id)
            sub = subscription_repository.reset_window_if_needed(db, sub)

            saved_projects = len(
                project_repository.get_all_projects(db, user_id)
            )

            plan = sub.plan
            is_pro = plan in (PLAN_PRO, PLAN_MAX) and sub.status == STATUS_ACTIVE
            is_max = plan == PLAN_MAX and sub.status == STATUS_ACTIVE

            limit = generation_limit_for_plan(plan)

            window_start = sub.generation_window_start or sub.created_at
            resets_at = (
                None
                if is_max
                else window_start + timedelta(days=GENERATION_WINDOW_DAYS)
            )

            return {
                "plan": plan,
                "status": sub.status,
                "expires_at": sub.expires_at,
                "generations_used": sub.generations_used,
                "generations_limit": limit,  # None for Max == unlimited
                "generations_period": "week",
                "resets_at": resets_at,
                "saved_projects": saved_projects,
                "is_pro": is_pro,
                "is_max": is_max,
                "can_export_pdf": is_pro,
                "can_generate_ideas": is_pro,
                "can_generate_llm_prompt": is_pro,
                "can_apply_ai_suggestions": is_pro,
                "can_edit_projects": is_pro,
                "can_use_architecture_agent": is_pro,
            }
        except Exception:
            logger.exception(
                f"Failed to compute subscription status for user {user_id}"
            )
            raise
        finally:
            db.close()

    # ------------------------------------------------------------ #
    # Upgrades
    # ------------------------------------------------------------ #

    def upgrade_plan(self, user_id: str, plan: str, months: int = 1):
        db = SessionLocal()
        try:
            return subscription_repository.upgrade_plan(db, user_id, plan, months)
        finally:
            db.close()

    def upgrade_to_pro(self, user_id: str, months: int = 1):
        """Kept for backwards compatibility -- thin wrapper."""
        return self.upgrade_plan(user_id, PLAN_PRO, months)

    def upgrade_to_max(self, user_id: str, months: int = 1):
        return self.upgrade_plan(user_id, PLAN_MAX, months)


subscription_service = SubscriptionService()


# ------------------------------------------------------------------ #
# FastAPI dependencies -- wire these into route signatures to enforce
# plan limits on the backend (never trust the frontend alone).
# ------------------------------------------------------------------ #

def require_pro(current_user=Depends(get_current_user)):
    """Use on routes gated to Pro AND Max: Idea Generator, Architecture
    Agent, PDF export, LLM Prompt Generator, AI suggestions, project
    editing."""

    if not subscription_service.is_pro(current_user["id"]):
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Upgrade to Pro",
                "reason": (
                    "This feature is available on the Pro and Max plans."
                ),
            },
        )

    return current_user


def require_max(current_user=Depends(get_current_user)):
    """Use on routes gated to Max only."""

    if not subscription_service.is_max(current_user["id"]):
        raise HTTPException(
            status_code=402,
            detail={
                "error": "Upgrade to Max",
                "reason": "This feature is available on the Max plan only.",
            },
        )

    return current_user


def require_generation_quota(current_user=Depends(get_current_user)):
    """Use on the project-generation route. Free gets
    FREE_PLAN_WEEKLY_GENERATION_LIMIT generations per rolling week,
    Pro gets PRO_PLAN_WEEKLY_GENERATION_LIMIT, Max is unlimited."""

    user_id = current_user["id"]

    if not subscription_service.can_generate(user_id):
        plan = subscription_service.get_plan(user_id)

        if plan == PLAN_PRO:
            reason = (
                f"You have used all {PRO_PLAN_WEEKLY_GENERATION_LIMIT} "
                f"generations this week. Upgrade to Max for unlimited "
                f"generations."
            )
        else:
            reason = (
                f"You have used all {FREE_PLAN_WEEKLY_GENERATION_LIMIT} "
                f"generations this week. Upgrade to Pro for "
                f"{PRO_PLAN_WEEKLY_GENERATION_LIMIT} generations/week or "
                f"Max for unlimited generations."
            )

        raise HTTPException(
            status_code=402,
            detail={
                "error": "Generation limit reached",
                "reason": reason,
            },
        )

    return current_user
