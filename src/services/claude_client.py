from anthropic import (
    Anthropic,
    RateLimitError as AnthropicRateLimitError,
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


class ClaudeClient:
    """Low-level Anthropic (Claude) API client. Same interface as
    GeminiClient/OpenAIClient so LLMManager can treat every provider
    identically."""

    def __init__(self):
        self.client = Anthropic(
            api_key=settings.ANTHROPIC_API_KEY,
            # We already retry across providers in LLMManager -- turn
            # off the SDK's own internal retries so failures surface
            # (and hand off to the next provider) immediately.
            max_retries=0,
        )

    def generate(
        self,
        prompt: str,
        model: str,
    ) -> str:
        """
        Send a prompt to Claude.

        Args:
            prompt: Prompt to send.
            model: Claude model name (e.g. "claude-sonnet-4-6").

        Returns:
            Generated text.

        Raises:
            RateLimitError: HTTP 429 (quota / rate limit exceeded).
            NonRetryableModelError: A permanent failure (bad key,
                insufficient credit balance, malformed request, no
                access to model) -- skip straight to the next provider.
            ModelUnavailableError: A transient failure (server error,
                overload, timeout, connection issue) -- worth retrying.
        """

        logger.info(f"Using model: {model}")

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )

            return "".join(
                block.text
                for block in response.content
                if getattr(block, "type", None) == "text"
            )

        except AnthropicRateLimitError as e:
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
                f"Claude permanently rejected the request for model "
                f"'{model}': {e}"
            ) from e

        except (APIStatusError, APIConnectionError) as e:
            raise ModelUnavailableError(
                f"Claude model '{model}' is currently unavailable: {e}"
            ) from e