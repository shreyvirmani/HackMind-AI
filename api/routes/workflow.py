from fastapi import APIRouter, HTTPException

from api.schemas import WorkflowRequest
from src.controllers.workflow_controller import workflow_controller
from src.services.project_service import project_service
from typing import List
from api.project_schemas import ProjectSummary

router = APIRouter(
    tags=["Workflow"],
)


# -------------------------
# Generate Project
# -------------------------

@router.post("/workflow")
def build_project(request: WorkflowRequest):
    return workflow_controller.build_project(
        request.idea
    )


# -------------------------
# Get All Projects
# -------------------------

@router.get(
    "/projects",
    response_model=List[ProjectSummary]
)
def get_projects():
    return project_service.get_all_projects()


# -------------------------
# Get Single Project
# -------------------------

@router.get("/projects/{project_id}")
def get_project(project_id: int):

    project = project_service.get_project(project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


# -------------------------
# Delete Project
# -------------------------

@router.delete("/projects/{project_id}")
def delete_project(project_id: int):

    project = project_service.delete_project(project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return {
        "message": "Project deleted successfully"
    }