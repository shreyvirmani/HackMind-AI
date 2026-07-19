from fastapi import APIRouter, Query

from src.services.project_service import project_service

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.get("")
def get_projects(
    user_id: str = Query(...)
):
    return project_service.get_all_projects(
        user_id=user_id
    )


@router.get("/{project_id}")
def get_project(
    project_id: int,
    user_id: str = Query(...)
):
    return project_service.get_project(
        project_id=project_id,
        user_id=user_id,
    )


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    user_id: str = Query(...)
):
    project_service.delete_project(
        project_id=project_id,
        user_id=user_id,
    )

    return {
        "status": "success"
    }