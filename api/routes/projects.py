from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.services.project_service import project_service
from src.auth.supabase_auth import get_current_user
from src.pdf.pdf_generator import pdf_generator


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


class ApplySuggestionRequest(BaseModel):
    section: str
    updated_data: dict


# =====================================================
# Get All Projects
# =====================================================

@router.get("")
def get_projects(
    current_user=Depends(get_current_user),
):
    return project_service.get_all_projects(
        user_id=current_user["id"],
    )


# =====================================================
# Get Single Project
# =====================================================

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


# =====================================================
# Apply AI Suggestion
# =====================================================

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


# =====================================================
# Delete Project
# =====================================================

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


# =====================================================
# Download PDF Report
# =====================================================

@router.get("/{project_id}/pdf")
def download_pdf(
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

    pdf_path = pdf_generator.generate(project)

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"{project.project_title}.pdf",
    )