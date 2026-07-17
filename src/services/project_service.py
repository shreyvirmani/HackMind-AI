from database.connection import SessionLocal
from database.repository import project_repository


class ProjectService:

    def save_project(
        self,
        idea,
        roadmap,
        research,
        judge,
        pitch_deck,
    ):
        db = SessionLocal()

        try:
            project = project_repository.create_project(
                db=db,
                project_title=roadmap.project_title,
                idea=idea,
                roadmap=roadmap.model_dump(),
                research=research.model_dump(),
                judge=judge.model_dump(),
                pitch_deck=pitch_deck.model_dump(),
            )

            return project

        finally:
            db.close()


    def get_all_projects(self):
        db = SessionLocal()

        try:
            return project_repository.get_all_projects(db)

        finally:
            db.close()


    def get_project(self, project_id: int):
        db = SessionLocal()

        try:
            return project_repository.get_project(
                db,
                project_id,
            )

        finally:
            db.close()


    def delete_project(self, project_id: int):
        db = SessionLocal()

        try:
            return project_repository.delete_project(
                db,
                project_id,
            )

        finally:
            db.close()


project_service = ProjectService()