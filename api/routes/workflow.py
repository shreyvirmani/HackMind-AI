from fastapi import APIRouter, Depends, BackgroundTasks
import uuid

from api.schemas import WorkflowRequest

from src.models.workflow_state import WorkflowState
from src.services.workflow_registry import workflow_registry
from src.services.workflow_runner import workflow_runner

from src.auth.supabase_auth import get_current_user


router = APIRouter(
    tags=["Workflow"],
)



# =====================================================
# Realtime Workflow Endpoint
# =====================================================

@router.post("/workflow/start")
async def start_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    """
    Starts AI workflow.

    Creates workflow session,
    runs agents in background,
    streams progress through WebSocket.
    """


    workflow_id = str(uuid.uuid4())


    workflow = WorkflowState(
        workflow_id=workflow_id,
        user_id=current_user["id"],
        idea=request.idea,
    )


    # Register workflow
    workflow_registry.create(
        workflow
    )


    # Run AI agents in background
    background_tasks.add_task(
        workflow_runner.run,
        workflow,
    )


    return {
        "status": "started",
        "workflow_id": workflow_id,
    }



# =====================================================
# Workflow Status Endpoint
# =====================================================

@router.get("/workflow/{workflow_id}")
def get_workflow(
    workflow_id: str,
):

    workflow = workflow_registry.get(
        workflow_id
    )


    if workflow is None:

        return {
            "status": "not_found"
        }



    return {

        "workflow_id":
            workflow.workflow_id,

        "planner":
            workflow.planner,

        "research":
            workflow.research,

        "judge":
            workflow.judge,

        "pitch":
            workflow.pitch,

        "finished":
            workflow.finished,

        "project_id":
            workflow.project_id,

        "error":
            workflow.error,
    }