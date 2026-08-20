from fastapi import APIRouter, Depends, HTTPException
import uuid

from api.schemas import WorkflowRequest

from src.services.workflow_service import workflow_service
from src.services.workflow_runner import workflow_runner

from src.auth.supabase_auth import get_current_user
from src.services.subscription_service import require_generation_quota


router = APIRouter(
    tags=["Workflow"],
)


# =====================================================
# Start a workflow
# =====================================================
# Unchanged contract: same request/response shape the frontend
# already sends and expects. Only the internals changed -- this now
# creates a DB row instead of an in-memory-only object, so it
# survives across separate serverless invocations.

@router.post("/workflow/start")
async def start_workflow(
    request: WorkflowRequest,
    current_user=Depends(require_generation_quota),
):
    workflow_id = str(uuid.uuid4())

    workflow_service.create(
        user_id=current_user["id"],
        idea=request.idea,
        workflow_id=workflow_id,
    )

    return {
        "status": "started",
        "workflow_id": workflow_id,
    }


# =====================================================
# Advance a workflow by exactly one stage
# =====================================================
# Replaces the old BackgroundTasks + WebSocket push. The frontend
# calls this repeatedly (once per stage) until `finished` is true --
# each call does at most one LLM stage's worth of work, safely inside
# any platform's function duration limit, and persists its result to
# the database immediately so progress is never lost even if a later
# call lands on a different server instance.

@router.post("/workflow/{workflow_id}/advance")
def advance_workflow(
    workflow_id: str,
    current_user=Depends(get_current_user),
):
    state = workflow_runner.advance(
        workflow_id=workflow_id,
        user_id=current_user["id"],
    )

    if state is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return state


# =====================================================
# Workflow Status Endpoint
# =====================================================
# Reads from the database now instead of the old in-memory registry,
# so it's safe to call from any instance. Auth added (the old
# in-memory version had none) so a workflow_id can't be polled by
# anyone other than the user who started it.

@router.get("/workflow/{workflow_id}")
def get_workflow(
    workflow_id: str,
    current_user=Depends(get_current_user),
):
    state = workflow_service.get_state(
        workflow_id=workflow_id,
        user_id=current_user["id"],
    )

    if state is None:
        return {"status": "not_found"}

    return state
