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
    """Raised when a model/provider is temporarily unavailable
    (overload, timeout, connection error). Worth retrying with
    backoff before moving to the next provider."""

    pass


class NonRetryableModelError(ModelUnavailableError):
    """Raised for permanent, non-transient failures on a provider --
    e.g. invalid/expired API key, insufficient billing credit, or a
    malformed request (HTTP 400/401/403/404). Retrying the same
    provider will never succeed, so the manager should skip straight
    to the next provider in the chain instead of retrying with
    backoff."""

    pass


class InvalidResponseError(LLMError):
    """Raised when the LLM returns an invalid response."""

    pass