import json
from pydantic import ValidationError
from src.exceptions.llm_exceptions import InvalidResponseError
from src.models.idea import IdeaResponse


def parse_ideas(response: str) -> IdeaResponse:
    try:
        text = response.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        result = IdeaResponse.model_validate(json.loads(text.strip()))
        if len(result.ideas) != 5:
            raise InvalidResponseError("Idea generator must return exactly 5 ideas.")
        return result
    except json.JSONDecodeError as exc:
        raise InvalidResponseError("Gemini returned invalid idea JSON.") from exc
    except ValidationError as exc:
        raise InvalidResponseError("Idea schema validation failed.") from exc
