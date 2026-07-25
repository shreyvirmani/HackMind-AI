from openai import (
    OpenAI,
    RateLimitError as GroqRateLimitError,
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


class GroqClient:
    """Low-level Groq API client.

    Groq's API is OpenAI-compatible, so this reuses the OpenAI SDK
    pointed at Groq's endpoint. Groq's free tier requires no credit
    card and no billing -- it's gated purely by rate limits, and only
    serves open-source models (Llama, GPT-OSS, etc), not GPT/Claude/
    Gemini. Same .generate(prompt, model) interface as the other
    clients so LLMManager can treat every provider identically.
    """

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
            # We already retry across providers in LLMManager -- turn
            # off the SDK's own internal retries so failures fail fast.
            max_retries=0,
        )

    def generate(
        self,
        prompt: str,
        model: str,
    ) -> str:
        """
        Send a prompt to Groq.

        Args:
            prompt: Prompt to send.
            model: Groq model name (e.g. "llama-3.3-70b-versatile").

        Returns:
            Generated text.

        Raises:
            RateLimitError: HTTP 429 (free-tier rate limit hit).
            NonRetryableModelError: A permanent failure (bad key,
                malformed request, model not available on Groq) --
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

        except GroqRateLimitError as e:
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
                f"Groq permanently rejected the request for model "
                f"'{model}': {e}"
            ) from e

        except (APIStatusError, APIConnectionError) as e:
            raise ModelUnavailableError(
                f"Groq model '{model}' is currently unavailable: {e}"
            ) from e