from fastapi import APIRouter, Depends

from api.chat_schemas import ChatRequest
from src.auth.supabase_auth import get_current_user

from src.controllers.chat_controller import chat_controller


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("")
def chat(
    request: ChatRequest,
    user=Depends(get_current_user),
):
    return chat_controller.chat(
        project_id=request.project_id,
        user_id=user["id"],
        message=request.message,
        history=request.history,
    )