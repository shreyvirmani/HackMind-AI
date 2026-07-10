import threading
import time

from src.config.settings import settings
from src.utils.logger import logger


class RateLimiter:
    """Simple thread-safe rate limiter."""

    def __init__(self):
        self.delay = settings.REQUEST_DELAY
        self.last_request_time = 0.0
        self.lock = threading.Lock()

    def wait(self):
        """
        Wait until enough time has passed since the last request.
        """

        with self.lock:

            current_time = time.time()
            elapsed = current_time - self.last_request_time

            if elapsed < self.delay:

                sleep_time = self.delay - elapsed

                logger.info(
                    f"Rate limiter waiting {sleep_time:.2f} seconds..."
                )

                time.sleep(sleep_time)

            self.last_request_time = time.time()


rate_limiter = RateLimiter()
