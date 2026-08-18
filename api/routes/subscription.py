from fastapi import APIRouter, Depends, HTTPException

from src.auth.supabase_auth import get_current_user
from src.services.subscription_service import subscription_service
from src.utils.logger import logger


router = APIRouter(
    prefix="/subscription",
    tags=["Subscription"],
)


@router.get("")
def get_subscription(current_user=Depends(get_current_user)):
    """
    The frontend calls this on load to decide what to show/allow --
    plan name, generations remaining, which premium features are
    unlocked, etc. This is a convenience for the UI; the backend still
    enforces limits independently on each protected route
    (require_pro / require_max / require_generation_quota), so this
    endpoint being wrong or skipped can't be used to bypass anything.
    """

    try:
        status = subscription_service.get_status(current_user["id"])
    except Exception as e:
        # Never let this bubble up as an opaque 500/503 -- log the
        # real cause server-side (subscription_service.get_status
        # already logs it too) and return a response the frontend can
        # actually show something useful for.
        logger.error(
            f"GET /subscription failed for user {current_user.get('id')}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Could not load subscription status. Please try again.",
        )

    return {
        "user_id": current_user["id"],
        **status,
    }
