from dataclasses import dataclass


@dataclass
class LLMRequest:
    prompt: str
    priority: str = "medium"
    cache_enabled: bool = True
    preferred_model: str | None = None
    max_retries: int = 3
    