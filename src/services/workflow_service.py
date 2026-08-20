from database.connection import SessionLocal
from database.repository import workflow_repository


def workflow_to_dict(workflow) -> dict:
    """Matches the exact response shape the frontend has always
    received from GET /workflow/{id}, so no frontend change is
    needed for that endpoint."""

    return {
        "workflow_id": workflow.id,
        "planner": workflow.planner,
        "research": workflow.research,
        "architecture": workflow.architecture,
        "judge": workflow.judge,
        "pitch": workflow.pitch,
        "finished": workflow.finished,
        "project_id": workflow.project_id,
        "error": workflow.error,
    }


class WorkflowService:

    def create(self, user_id: str, idea: str, workflow_id: str) -> dict:
        db = SessionLocal()

        try:
            workflow = workflow_repository.create(
                db=db,
                workflow_id=workflow_id,
                user_id=user_id,
                idea=idea,
            )

            return workflow_to_dict(workflow)

        finally:
            db.close()

    def get_state(self, workflow_id: str, user_id: str | None = None) -> dict | None:
        db = SessionLocal()

        try:
            workflow = workflow_repository.get(db, workflow_id, user_id)

            if workflow is None:
                return None

            return workflow_to_dict(workflow)

        finally:
            db.close()


workflow_service = WorkflowService()
