from api.chat_schemas import ChatMessage

from src.services.chat_service import chat_service


class ChatController:

    def chat(
        self,
        project_id: int,
        user_id: str,
        message: str,
        history: list[ChatMessage],
    ):
        return chat_service.chat(
            project_id=project_id,
            user_id=user_id,
            message=message,
            history=history,
        )


chat_controller = ChatController()