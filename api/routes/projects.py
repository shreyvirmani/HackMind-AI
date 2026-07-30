import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError

from src.services.project_service import project_service
from src.auth.supabase_auth import get_current_user
from src.services.subscription_service import require_pro
from src.pdf.pdf_generator import PDFGenerator


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



@router.get("/{project_id}/pdf")
def download_project_pdf(
    project_id: int,
    current_user=Depends(require_pro),
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

    try:
        pdf_buffer = PDFGenerator(project)

    except ValidationError:
        # roadmap/research/judge/pitch_deck haven't been fully
        # generated yet for this project, so there isn't enough data
        # for a complete report.
        raise HTTPException(
            status_code=422,
            detail=(
                "This project isn't fully generated yet, so a PDF "
                "report can't be created. Run the full workflow "
                "(planner, research, judge, pitch deck) first."
            ),
        )

    safe_title = re.sub(
        r"[^a-zA-Z0-9_-]+", "_", project.project_title or "project"
    ).strip("_") or "project"

    filename = f"{safe_title}_report.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.post("/{project_id}/apply-suggestion")
def apply_suggestion(
    project_id: int,
    request: ApplySuggestionRequest,
    current_user=Depends(require_pro),
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