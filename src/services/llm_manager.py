import time
from dataclasses import dataclass

from src.config.settings import settings

from src.models.llm_request import LLMRequest
from src.models.llm_response import LLMResponse

from src.services.cache import cache
from src.services.gemini_client import GeminiClient
from src.services.groq_client import GroqClient
from src.services.openai_client import OpenAIClient
from src.services.claude_client import ClaudeClient
from src.services.rate_limiter import RateLimiter
from src.services.circuit_breaker import CircuitBreaker
from src.services.telemetry import telemetry

from src.exceptions.llm_exceptions import (
    RateLimitError,
    ModelUnavailableError,
    NonRetryableModelError,
    CircuitOpenError,
)

from src.utils.logger import logger


@dataclass
class ProviderStep:
    provider: str      # "gemini" | "openai" | "claude" -- for logs/telemetry
    model: str          # model name to send to that provider
    client: object       # the client instance with a .generate(prompt, model)


class LLMManager:
    """
    Routes generation requests across multiple free-tier LLM
    providers, in this order:

        Gemini (key 1) -> Gemini (key 2) -> Groq -> [OpenAI] -> [Claude]

    Why two Gemini keys: Gemini's free quota is tracked per API
    key/project, so a second free key from a separate Google AI
    Studio project effectively doubles the free request budget at no
    cost -- it isn't just retrying the same limited pool.

    Why Groq: it's a genuinely different provider/infrastructure with
    its own free, no-card-required tier, so a Google-side outage or
    quota exhaustion can't take the whole chain down with it.

    OpenAI and Claude are included but OPTIONAL and treated as paid
    extras -- they only join the chain if OPENAI_API_KEY /
    ANTHROPIC_API_KEY are set. Leave them blank to stay on 100% free
    tiers.

    Each provider gets its own rate limiter and circuit breaker, so
    one provider being throttled doesn't slow down or block traffic
    meant for the others.
    """

    def __init__(self):

        self.gemini_client = GeminiClient(api_key=settings.GOOGLE_API_KEY)
        self.gemini_client_2 = (
            GeminiClient(api_key=settings.GOOGLE_API_KEY_2)
            if settings.GOOGLE_API_KEY_2
            else None
        )
        self.groq_client = GroqClient() if settings.GROQ_API_KEY else None
        self.openai_client = OpenAIClient() if settings.OPENAI_API_KEY else None
        self.claude_client = ClaudeClient() if settings.ANTHROPIC_API_KEY else None

        candidate_chain = [
            ProviderStep("gemini", settings.PRIMARY_MODEL, self.gemini_client),
            ProviderStep("gemini-2", settings.SECONDARY_MODEL, self.gemini_client_2),
            ProviderStep("groq", settings.GROQ_MODEL, self.groq_client),
            ProviderStep("openai", settings.TERTIARY_MODEL, self.openai_client),
            ProviderStep("claude", settings.QUATERNARY_MODEL, self.claude_client),
        ]

        self.chain: list[ProviderStep] = []
        for step in candidate_chain:
            if step.client is None:
                logger.info(
                    f"Skipping provider '{step.provider}' in the LLM "
                    f"fallback chain -- no API key configured for it."
                )
                continue
            self.chain.append(step)

        if not self.chain:
            raise ModelUnavailableError(
                "No LLM providers are configured. Set at least "
                "GOOGLE_API_KEY in your environment."
            )

        logger.info(
            "LLM fallback chain: "
            + " -> ".join(f"{s.provider}:{s.model}" for s in self.chain)
        )

        # One rate limiter + circuit breaker PER provider, so one
        # provider being throttled doesn't slow down or block traffic
        # meant for the others.
        self.rate_limiters = {
            step.provider: RateLimiter() for step in self.chain
        }
        self.circuit_breakers = {
            step.provider: CircuitBreaker() for step in self.chain
        }

    def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        telemetry.increment("total_requests")

        # ---------------- Cache ---------------- #

        if request.cache_enabled:

            cached = cache.get(request.prompt)

            if cached is not None:

                telemetry.increment("cache_hits")
                logger.info("Cache HIT")

                return LLMResponse(
                    content=cached,
                    model="CACHE",
                    cached=True,
                    retries=0,
                    response_time=0.0,
                )

            telemetry.increment("cache_misses")

        logger.info("Cache MISS")

        # --------------- Multi-provider fallback --------------- #

        start = time.perf_counter()
        total_retries = 0
        last_error: Exception | None = None

        for attempt_index, step in enumerate(self.chain):

            breaker = self.circuit_breakers[step.provider]
            limiter = self.rate_limiters[step.provider]

            if not breaker.allow_request():
                logger.warning(
                    f"Skipping '{step.provider}': circuit breaker OPEN."
                )
                last_error = CircuitOpenError(
                    f"Circuit breaker open for '{step.provider}'."
                )
                continue

            per_provider_retries = max(1, request.max_retries)

            for retry in range(per_provider_retries):

                try:
                    limiter.wait()

                    content = step.client.generate(
                        prompt=request.prompt,
                        model=step.model,
                    )

                    breaker.record_success()

                    elapsed = round(time.perf_counter() - start, 3)

                    telemetry.increment("successful_requests")
                    telemetry.add_response_time(elapsed)

                    if attempt_index > 0:
                        telemetry.increment("fallbacks")
                        logger.info(
                            f"Fell back to '{step.provider}' "
                            f"({step.model}) after earlier provider(s) "
                            f"failed."
                        )

                    if request.cache_enabled:
                        cache.set(request.prompt, content)

                    return LLMResponse(
                        content=content,
                        model=f"{step.provider}:{step.model}",
                        cached=False,
                        retries=total_retries,
                        response_time=elapsed,
                    )

                except RateLimitError as e:
                    # 429 means this provider's quota is exhausted
                    # right now -- retrying it won't help, move
                    # straight on to the next provider in the chain.
                    logger.warning(
                        f"Rate limited on '{step.provider}' "
                        f"({step.model}): {e}"
                    )
                    breaker.record_failure()
                    last_error = e
                    break

                except NonRetryableModelError as e:
                    # Permanent failure (bad key, no billing credit,
                    # malformed request) -- retrying this provider
                    # will never succeed, so don't waste time/backoff
                    # on it. Move straight to the next provider.
                    logger.warning(
                        f"'{step.provider}' ({step.model}) permanently "
                        f"unavailable, skipping remaining retries: {e}"
                    )
                    breaker.record_failure()
                    last_error = e
                    break

                except ModelUnavailableError as e:
                    # Transient failure (overload, timeout, connection
                    # issue) -- worth a couple of retries with backoff
                    # before giving up on this provider.
                    logger.warning(
                        f"'{step.provider}' ({step.model}) unavailable "
                        f"(attempt {retry + 1}/{per_provider_retries}): {e}"
                    )
                    breaker.record_failure()
                    last_error = e
                    total_retries += 1
                    telemetry.increment("retries")

                    if retry < per_provider_retries - 1:
                        time.sleep(min(2 ** retry, 8))

                    continue

        # Every provider in the chain failed.
        telemetry.increment("failed_requests")

        raise ModelUnavailableError(
            "All configured LLM providers failed (rate-limited or "
            f"unavailable). Last error: {last_error}"
        ) from last_error


llm = LLMManager()