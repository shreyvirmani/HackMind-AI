class LLMError(Exception):
    """Base LLM exception."""


class RateLimitError(LLMError):
    """Raised when all retries fail due to rate limiting."""


class ModelUnavailableError(LLMError):
    """Raised when no model is available."""


class CircuitOpenError(LLMError):
    """Raised when the circuit breaker is open."""