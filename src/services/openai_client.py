from openai import (
    OpenAI,
    RateLimitError as OpenAIRateLimitError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    BadRequestError,
    UnprocessableEntityError,
    APIStatusError,
    APIConnectionError,
)

from src.config.settings import settings
from src.utils.logger import logger
from src.exceptions.llm_exceptions import (
    ModelUnavailableError,
    NonRetryableModelError,
    RateLimitError,
)


class OpenAIClient:
    """Low-level OpenAI API client. Same interface as GeminiClient so
    LLMManager can treat every provider identically."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            # We already retry across providers in LLMManager -- turn
            # off the SDK's own internal retries so a 429 fails fast
            # and hands off to the next provider immediately instead
            # of silently burning several seconds first.
            max_retries=0,
        )

    def generate(
        self,
        prompt: str,
        model: str,
    ) -> str:
        """
        Send a prompt to OpenAI.

        Args:
            prompt: Prompt to send.
            model: OpenAI model name (e.g. "gpt-4o-mini").

        Returns:
            Generated text.

        Raises:
            RateLimitError: HTTP 429 (quota / rate limit exceeded).
            NonRetryableModelError: A permanent failure (bad key,
                billing, malformed request, no access to model) --
                skip straight to the next provider.
            ModelUnavailableError: A transient failure (server error,
                timeout, connection issue) -- worth retrying.
        """

        logger.info(f"Using model: {model}")

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )

            return response.choices[0].message.content

        except OpenAIRateLimitError as e:
            raise RateLimitError(
                f"Rate limit hit for model '{model}'."
            ) from e

        except (
            AuthenticationError,
            PermissionDeniedError,
            NotFoundError,
            BadRequestError,
            UnprocessableEntityError,
        ) as e:
            raise NonRetryableModelError(
                f"OpenAI permanently rejected the request for model "
                f"'{model}': {e}"
            ) from e

        except (APIStatusError, APIConnectionError) as e:
            raise ModelUnavailableError(
                f"OpenAI model '{model}' is currently unavailable: {e}"
            ) from e