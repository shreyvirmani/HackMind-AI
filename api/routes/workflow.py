from fastapi import APIRouter, Depends

from api.schemas import WorkflowRequest
from src.controllers.workflow_controller import workflow_controller
from src.auth.supabase_auth import get_current_user

router = APIRouter(
    tags=["Workflow"],
)


@router.post("/workflow")
def build_project(
    request: WorkflowRequest,
    current_user=Depends(get_current_user),
):
    return workflow_controller.build_project(
        idea=request.idea,
        user_id=current_user["id"],
    )