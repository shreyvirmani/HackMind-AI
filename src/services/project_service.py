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
                roadmap=roadmap.model_dump() if roadmap else {},
                research=research.model_dump() if research else {},
                judge=judge.model_dump() if judge else {},
                pitch_deck=pitch_deck.model_dump() if pitch_deck else {},
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


    def apply_suggestion(
        self,
        project_id,
        user_id,
        section,
        updated_data,
    ):
        db = SessionLocal()

        try:
            return project_repository.update_project_section(
                db=db,
                project_id=project_id,
                user_id=user_id,
                section=section,
                updated_data=updated_data,
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