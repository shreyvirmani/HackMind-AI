from sqlalchemy.orm import Session

from .models import Project


class ProjectRepository:

    def create_project(
        self,
        db: Session,
        user_id: str,
        project_title: str,
        idea: str,
        roadmap: dict,
        research: dict,
        judge: dict,
        pitch_deck: dict,
    ):

        overall_score = (
            judge.get("overall_score", 0)
            if isinstance(judge, dict)
            else 0
        )

        project = Project(
            user_id=user_id,
            project_title=project_title,
            idea=idea,
            roadmap=roadmap,
            research=research,
            judge=judge,
            pitch_deck=pitch_deck,
            overall_score=overall_score,
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    def get_all_projects(
        self,
        db: Session,
        user_id: str,
    ):

        return (
            db.query(Project)
            .filter(Project.user_id == user_id)
            .order_by(Project.created_at.desc())
            .all()
        )

    def get_project(
        self,
        db: Session,
        project_id: int,
        user_id: str,
    ):

        return (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.user_id == user_id,
            )
            .first()
        )

    def delete_project(
        self,
        db: Session,
        project_id: int,
        user_id: str,
    ):

        project = self.get_project(
            db,
            project_id,
            user_id,
        )

        if project:
            db.delete(project)
            db.commit()

        return project


project_repository = ProjectRepository()