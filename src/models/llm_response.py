from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    model: str
    cached: bool
    retries: int
    response_time: float