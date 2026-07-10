import hashlib
import time


class MemoryCache:
    """Stores Gemini responses temporarily."""

    def __init__(self):
        self.cache = {}

    def _hash(self, prompt: str) -> str:
        """
        Convert a prompt into a unique hash key.
        """
        return hashlib.sha256(prompt.encode()).hexdigest()

    def get(self, prompt: str):

        key = self._hash(prompt)

        if key not in self.cache:
            return None

        value, expiry = self.cache[key]

        if time.time() > expiry:
            del self.cache[key]
            return None

        return value

    def set(
        self,
        prompt: str,
        value: str,
        ttl: int = 600,
    ):
        """
        Cache response for ttl seconds.
        """

        key = self._hash(prompt)

        self.cache[key] = (
            value,
            time.time() + ttl,
        )

    def clear(self):
        """Clear entire cache."""

        self.cache.clear()


cache = MemoryCache()
