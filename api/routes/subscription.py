from fastapi import APIRouter, Depends

from src.auth.supabase_auth import get_current_user
from src.services.subscription_service import subscription_service


router = APIRouter(
    prefix="/subscription",
    tags=["Subscription"],
)


@router.get("")
def get_subscription(current_user=Depends(get_current_user)):
    """
    The frontend calls this on load to decide what to show/allow --
    e.g. "Projects Remaining 1/2", whether to show the PDF export
    button, whether AI suggestions are enabled, etc. This is a
    convenience for the UI; the backend still enforces limits
    independently on each protected route (require_pro /
    require_generation_quota), so this endpoint being wrong or
    skipped can't be used to bypass anything.
    """

    status = subscription_service.get_status(current_user["id"])

    return {
        "user_id": current_user["id"],
        **status,
    }