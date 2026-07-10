import time

from src.utils.logger import logger


class CircuitBreaker:

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 60,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0

        self.last_failure_time = None

        self.state = "CLOSED"

    def allow_request(self) -> bool:
        """
        Determines whether a request can proceed.
        """

        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":

            elapsed = time.time() - self.last_failure_time

            if elapsed >= self.recovery_timeout:

                logger.info(
                    "Circuit Breaker entering HALF-OPEN state."
                )

                self.state = "HALF_OPEN"

                return True

            return False

        if self.state == "HALF_OPEN":
            return True

        return True

    def record_success(self):

        self.failure_count = 0

        self.state = "CLOSED"

        logger.info(
            "Circuit Breaker reset."
        )

    def record_failure(self):

        self.failure_count += 1

        self.last_failure_time = time.time()

        logger.warning(
            f"Failure count: {self.failure_count}"
        )

        if self.failure_count >= self.failure_threshold:

            self.state = "OPEN"

            logger.error(
                "Circuit Breaker OPEN."
            )


circuit_breaker = CircuitBreaker()
