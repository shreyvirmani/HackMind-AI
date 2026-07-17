from fastapi import APIRouter

from src.services.project_service import project_service

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.get("")
def get_projects():
    return project_service.get_projects()


@router.get("/{project_id}")
def get_project(project_id: int):
    return project_service.get_project(project_id)


@router.delete("/{project_id}")
def delete_project(project_id: int):
    project_service.delete_project(project_id)

    return {
        "status": "success"
    }