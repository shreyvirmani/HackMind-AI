from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.services.subscription_service import require_pro
from src.controllers.idea_controller import idea_controller


router = APIRouter(prefix="/ideas", tags=["Ideas"])


class IdeaRequest(BaseModel):
    context: str = Field(default="", max_length=5000)


@router.post("/generate")
def generate_ideas(request: IdeaRequest, current_user=Depends(require_pro)):
    context = request.context.strip() or "Generate useful, original student and hackathon project ideas."
    return idea_controller.generate(context)
