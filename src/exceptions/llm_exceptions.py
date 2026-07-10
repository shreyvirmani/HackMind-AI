class LLMError(Exception):
    """Base exception for all LLM-related errors."""

    pass


class CircuitOpenError(LLMError):
    """Raised when the circuit breaker is open."""

    pass


class RateLimitError(LLMError):
    """Raised when the API rate limit has been exceeded."""

    pass


class ModelUnavailableError(LLMError):
    """Raised when no Gemini model is available."""

    pass


class InvalidResponseError(LLMError):
    """Raised when the LLM returns an invalid response."""

    pass