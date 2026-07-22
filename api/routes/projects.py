from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.services.project_service import project_service
from src.auth.supabase_auth import get_current_user


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)



class ApplySuggestionRequest(BaseModel):
    section: str
    updated_data: dict



@router.get("")
def get_projects(
    current_user=Depends(get_current_user),
):
    return project_service.get_all_projects(
        user_id=current_user["id"],
    )



@router.get("/{project_id}")
def get_project(
    project_id: int,
    current_user=Depends(get_current_user),
):

    project = project_service.get_project(
        project_id=project_id,
        user_id=current_user["id"],
    )


    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )


    return project



@router.post("/{project_id}/apply-suggestion")
def apply_suggestion(
    project_id: int,
    request: ApplySuggestionRequest,
    current_user=Depends(get_current_user),
):

    project = project_service.apply_suggestion(
        project_id=project_id,
        user_id=current_user["id"],
        section=request.section,
        updated_data=request.updated_data,
    )


    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )


    return {
        "status": "success",
        "message": "AI suggestion applied successfully",
        "project": project,
    }



@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    current_user=Depends(get_current_user),
):

    project = project_service.delete_project(
        project_id=project_id,
        user_id=current_user["id"],
    )


    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )


    return {
        "status": "success"
    }