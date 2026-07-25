from google import genai
from google.genai.errors import ClientError, ServerError

from src.config.settings import settings
from src.utils.logger import logger
from src.exceptions.llm_exceptions import (
    ModelUnavailableError,
    NonRetryableModelError,
    RateLimitError,
)

# HTTP codes that mean "this will never succeed on retry" -- bad/expired
# key, no access to the model, malformed request, etc. Anything else
# (5xx, overload) is treated as transient and worth retrying.
_PERMANENT_CODES = {400, 401, 403, 404}


class GeminiClient:
    """Low-level Gemini API client."""

    def __init__(self, api_key: str | None = None):
        self.client = genai.Client(
            api_key=api_key or settings.GOOGLE_API_KEY
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

        Raises:
            RateLimitError: The model returned HTTP 429 (quota exceeded).
            NonRetryableModelError: A permanent failure (bad key,
                billing, malformed request) -- skip straight to the
                next provider, don't retry this one.
            ModelUnavailableError: A transient failure (overload,
                server error) -- worth retrying with backoff.
        """

        logger.info(f"Using model: {model}")

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
            )

            return response.text

        except ClientError as e:
            code = getattr(e, "code", None)

            if code == 429:
                raise RateLimitError(
                    f"Rate limit hit for model '{model}'."
                ) from e

            if code in _PERMANENT_CODES:
                raise NonRetryableModelError(
                    f"Gemini permanently rejected the request for "
                    f"model '{model}': {e}"
                ) from e

            raise ModelUnavailableError(
                f"Gemini rejected the request for model '{model}': {e}"
            ) from e

        except ServerError as e:
            raise ModelUnavailableError(
                f"Gemini model '{model}' is currently overloaded."
            ) from e