from abc import ABC, abstractmethod

from src.models.llm_request import LLMRequest
from src.services.llm_manager import llm


class BaseAgent(ABC):

    def __init__(self):

        self.llm = llm

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """
        Every agent defines its own prompt.
        """

    def run(
        self,
        user_input: str,
    ):

        prompt = f"""
{self.system_prompt}

USER INPUT:

{user_input}
"""

        request = LLMRequest(
            prompt=prompt,
            priority="high",
            cache_enabled=True,
        )

        response = self.llm.generate(request)

        return response.content