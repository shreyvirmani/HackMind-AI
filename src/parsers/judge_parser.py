import json

from pydantic import ValidationError

from src.exceptions.llm_exceptions import InvalidResponseError
from src.models.judge import JudgeReport


def parse_judge(response: str) -> JudgeReport:
    """
    Parse Gemini response into a validated JudgeReport model.
    """

    try:

        from src.parsers.utils import extract_json
        text = extract_json(response)
        data = json.loads(text)

        return JudgeReport.model_validate(data)

    except json.JSONDecodeError as e:

        raise InvalidResponseError(
            "Gemini returned invalid JSON."
        ) from e

    except ValidationError as e:

        raise InvalidResponseError(
            "Judge report schema validation failed."
        ) from e