import time

from src.models.llm_request import LLMRequest
from src.models.llm_response import LLMResponse

from src.services.cache import cache
from src.services.gemini_client import GeminiClient
from src.services.rate_limiter import rate_limiter
from src.services.telemetry import telemetry

from src.utils.logger import logger


class LLMManager:

    def __init__(self):

        self.client = GeminiClient()

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

        # --------------- API Call --------------- #

        rate_limiter.wait()

        start = time.perf_counter()

        response = self.client.generate(
            prompt=request.prompt,
            model=request.preferred_model or "gemini-2.5-flash",
        )

        elapsed = round(time.perf_counter() - start, 3)

        telemetry.increment("successful_requests")
        telemetry.add_response_time(elapsed)

        if request.cache_enabled:
            cache.set(request.prompt, response)

        return LLMResponse(
            content=response,
            model=request.preferred_model or "gemini-2.5-flash",
            cached=False,
            retries=0,
            response_time=elapsed,
        )


llm = LLMManager()