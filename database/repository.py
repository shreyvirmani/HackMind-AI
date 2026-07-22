from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

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



    def update_project_section(
        self,
        db: Session,
        project_id: int,
        user_id: str,
        section: str,
        updated_data: dict,
    ):

        project = self.get_project(
            db,
            project_id,
            user_id,
        )


        if not project:
            return None



        if section == "roadmap":

            current_data = project.roadmap or {}

            current_data.update(updated_data)

            project.roadmap = current_data

            flag_modified(
                project,
                "roadmap"
            )



        elif section == "research":

            current_data = project.research or {}

            current_data.update(updated_data)

            project.research = current_data

            flag_modified(
                project,
                "research"
            )



        elif section == "judge":

            current_data = project.judge or {}

            current_data.update(updated_data)

            project.judge = current_data

            flag_modified(
                project,
                "judge"
            )



        elif section == "pitch_deck":

            current_data = project.pitch_deck or {}

            current_data.update(updated_data)

            project.pitch_deck = current_data

            flag_modified(
                project,
                "pitch_deck"
            )



        else:

            raise ValueError(
                f"Invalid section: {section}"
            )



        db.commit()

        db.refresh(project)


        return project





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