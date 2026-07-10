from src.services.cache import cache
from src.services.circuit_breaker import circuit_breaker
from src.services.rate_limiter import rate_limiter
from src.services.telemetry import telemetry
from src.exceptions.llm_exceptions import CircuitOpenError
from src.models.llm_request import LLMRequest
from src.models.llm_response import LLMResponse
from src.utils.logger import logger


class RequestHandler:

    def prepare(
        self,
        request: LLMRequest,
    ) -> LLMResponse | None:
        """
        Prepare an LLM request.

        Returns:
            Cached response if available,
            otherwise None.
        """

        telemetry.increment("total_requests")

        if request.cache_enabled:

            cached = cache.get(request.prompt)

            if cached:

                telemetry.increment("cache_hits")

                logger.info("Cache HIT")

                return LLMResponse(
                    content=cached,
                    model="CACHE",
                    cached=True,
                    retries=0,
                    response_time=0,
                )

            telemetry.increment("cache_misses")

        if not circuit_breaker.allow_request():

            raise CircuitOpenError(
                "Circuit breaker is OPEN."
            )

        rate_limiter.wait()

        return None


request_handler = RequestHandler()