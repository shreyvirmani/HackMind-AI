import json

from pydantic import ValidationError

from src.models.roadmap import Roadmap
from src.exceptions.llm_exceptions import InvalidResponseError


def parse_roadmap(response: str) -> Roadmap:
    """
    Parse Gemini response into a validated Roadmap model.
    """

    try:
        response = response.strip()

        if response.startswith("```json"):
            response = response.replace("```json", "", 1)

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        data = json.loads(response)

        return Roadmap.model_validate(data)

    except json.JSONDecodeError as e:
        raise InvalidResponseError(
            "Gemini returned invalid JSON."
        ) from e

    except ValidationError as e:
        raise InvalidResponseError(
            "Roadmap schema validation failed."
        ) from e