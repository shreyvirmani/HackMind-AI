import json

from pydantic import ValidationError

from src.exceptions.llm_exceptions import InvalidResponseError
from src.models.research import ResearchReport


def parse_research(response: str) -> ResearchReport:
    """
    Parse Gemini response into a validated ResearchReport.
    """

    try:
        from src.parsers.utils import extract_json
        text = extract_json(response)
        data = json.loads(text)

        return ResearchReport.model_validate(data)

    except json.JSONDecodeError as e:
        raise InvalidResponseError(
            "Gemini returned invalid research JSON."
        ) from e

    except ValidationError as e:
        raise InvalidResponseError(
            "Research schema validation failed."
        ) from e