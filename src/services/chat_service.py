from api.chat_schemas import ChatMessage

from database.connection import SessionLocal
from database.repository import project_repository

from src.agents.copilot_agent import copilot_agent


class ChatService:

    def chat(
        self,
        project_id: int,
        user_id: str,
        message: str,
        history: list[ChatMessage],
    ):

        db = SessionLocal()

        try:

            project = project_repository.get_project(
                db=db,
                project_id=project_id,
                user_id=user_id,
            )


            if not project:

                return {
                    "response": "Project not found."
                }



            context = f"""
Project Title:
{project.project_title}

Idea:
{project.idea}

Roadmap:
{project.roadmap}

Research:
{project.research}

Judge:
{project.judge}

Pitch Deck:
{project.pitch_deck}
"""



            answer = copilot_agent.chat(
                project_context=context,
                history=history,
                user_message=message,
            )



            suggestion = None



            # Detect structured suggestion from AI response
            if isinstance(answer, dict):

                suggestion = answer.get(
                    "suggestion"
                )

                response_text = answer.get(
                    "response",
                    ""
                )

            else:

                response_text = answer



            return {

                "response": response_text,

                "suggestion": suggestion,

            }



        finally:

            db.close()



chat_service = ChatService()