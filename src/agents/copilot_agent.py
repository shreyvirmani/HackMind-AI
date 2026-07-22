from api.chat_schemas import ChatMessage

import json

from src.agents.base_agent import BaseAgent
from src.models.llm_request import LLMRequest
from src.utils.logger import logger
from src.config.settings import settings



class CopilotAgent(BaseAgent):


    @property
    def system_prompt(self) -> str:

        return """
You are HackMind AI Copilot.

You already know everything about the user's current hackathon project.

Your responsibilities:

• Improve project ideas
• Improve roadmap
• Suggest features
• Explain judge feedback
• Improve hackathon score
• Suggest monetization
• Improve pitch
• Help with technical implementation
• Answer questions naturally

Never say you don't know the project.

Always answer as the project's AI teammate.

Use the conversation history to maintain context.

If the user asks follow-up questions like:
"improve it"
"explain more"
"change phase 2"
"make it better"

understand what "it" refers to from the previous conversation.


IMPORTANT:

When your answer contains a practical improvement that can modify the project, return JSON only:

{
  "response": "Human readable explanation",
  "suggestion": {
      "section": "roadmap | research | judge | pitch_deck",
      "updated_data": {}
  }
}


If no project update is needed, return:

{
  "response": "Your answer here",
  "suggestion": null
}


Never add markdown outside JSON.

Keep answers concise unless the user requests detail.
"""



    def chat(
        self,
        project_context: str,
        history: list[ChatMessage],
        user_message: str,
    ) -> dict:


        logger.info(
            "CopilotAgent started"
        )


        conversation = ""


        for msg in history:

            speaker = (
                "User"
                if msg.role == "user"
                else "Assistant"
            )

            conversation += (
                f"{speaker}: {msg.content}\n"
            )



        prompt = f"""
{self.system_prompt}

====================================================

PROJECT CONTEXT

{project_context}

====================================================

CONVERSATION HISTORY

{conversation}

====================================================

CURRENT USER MESSAGE

{user_message}

====================================================

Return only valid JSON.
"""



        models_to_try = [
            settings.SECONDARY_MODEL,
            settings.TERTIARY_MODEL,
            settings.PRIMARY_MODEL,
        ]


        last_error = None



        for model in models_to_try:

            try:

                logger.info(
                    f"Trying model: {model}"
                )


                request = LLMRequest(
                    prompt=prompt,
                    preferred_model=model,
                    cache_enabled=True,
                )


                response = self.llm.generate(
                    request
                )


                logger.info(
                    f"CopilotAgent completed using {model}"
                )



                raw_content = response.content.strip()



                try:

                    parsed = json.loads(
                        raw_content
                    )

                    return parsed


                except json.JSONDecodeError:

                    logger.warning(
                        "AI returned invalid JSON, using fallback"
                    )


                    return {
                        "response": raw_content,
                        "suggestion": None,
                    }



            except Exception as e:


                logger.warning(
                    f"{model} failed: {e}"
                )


                last_error = e



        logger.error(
            "All Copilot models failed."
        )


        raise last_error




copilot_agent = CopilotAgent()