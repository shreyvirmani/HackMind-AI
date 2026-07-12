from abc import ABC, abstractmethod

from src.models.llm_request import LLMRequest
from src.services.llm_manager import llm
from src.utils.logger import logger


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
    ) -> str:

        logger.info(f"{self.__class__.__name__} started")

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

        logger.info(f"{self.__class__.__name__} completed")

        return response.content