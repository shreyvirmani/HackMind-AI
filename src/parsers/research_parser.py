import json

from pydantic import ValidationError

from src.exceptions.llm_exceptions import InvalidResponseError
from src.models.research import ResearchReport


def parse_research(response: str) -> ResearchReport:
    """
    Parse Gemini response into a validated ResearchReport.
    """

    try:
        response = response.strip()

        if response.startswith("```json"):
            response = response.replace("```json", "", 1)

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        data = json.loads(response)

        return ResearchReport.model_validate(data)

    except json.JSONDecodeError as e:
        raise InvalidResponseError(
            "Gemini returned invalid research JSON."
        ) from e

    except ValidationError as e:
        raise InvalidResponseError(
            "Research schema validation failed."
        ) from e