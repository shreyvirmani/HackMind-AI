from database.connection import SessionLocal
from database.repository import project_repository


class ProjectService:

    def save_project(
        self,
        user_id,
        idea,
        roadmap,
        research,
        judge,
        pitch_deck,
    ):
        db = SessionLocal()

        try:
            return project_repository.create_project(
                db=db,
                user_id=user_id,
                project_title=roadmap.project_title,
                idea=idea,
                roadmap=roadmap.model_dump(),
                research=research.model_dump(),
                judge=judge.model_dump(),
                pitch_deck=pitch_deck.model_dump(),
            )
        finally:
            db.close()

    def get_all_projects(
        self,
        user_id,
    ):
        db = SessionLocal()

        try:
            return project_repository.get_all_projects(
                db,
                user_id,
            )
        finally:
            db.close()

    def get_project(
        self,
        project_id,
        user_id,
    ):
        db = SessionLocal()

        try:
            return project_repository.get_project(
                db,
                project_id,
                user_id,
            )
        finally:
            db.close()

    def delete_project(
        self,
        project_id,
        user_id,
    ):
        db = SessionLocal()

        try:
            return project_repository.delete_project(
                db,
                project_id,
                user_id,
            )
        finally:
            db.close()


project_service = ProjectService()