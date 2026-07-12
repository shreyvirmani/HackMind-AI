from google import genai

from src.config.settings import settings
from src.utils.logger import logger
from src.exceptions.llm_exceptions import ModelUnavailableError

class GeminiClient:
    """Low-level Gemini API client."""

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GOOGLE_API_KEY
        )

    def generate(
        self,
        prompt: str,
        model: str,
    ) -> str:
        """
        Send a prompt to Gemini.

        Args:
            prompt: Prompt to send.
            model: Gemini model name.

        Returns:
            Generated text.
        """

        logger.info(f"Using model: {model}")

        from google.genai.errors import ServerError

        ...

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
            )

            return response.text

        except ServerError:
            raise ModelUnavailableError(
                "Gemini is currently overloaded. Please try again in a few moments."
            )