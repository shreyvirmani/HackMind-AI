import json
import re

from pydantic import ValidationError

from src.models.roadmap import Roadmap
from src.exceptions.llm_exceptions import InvalidResponseError


from src.parsers.utils import extract_json

def parse_roadmap(response: str) -> Roadmap:
    """
    Parse roadmap returned by any LLM.
    """

    try:

        cleaned = extract_json(response)

        data = json.loads(cleaned)

        return Roadmap.model_validate(data)

    except json.JSONDecodeError as e:

        print("=" * 80)
        print("RAW MODEL RESPONSE")
        print(response)
        print("=" * 80)

        raise InvalidResponseError(
            "Model returned invalid JSON."
        ) from e

    except ValidationError as e:

        print("=" * 80)
        print("VALIDATION ERROR")
        print(e)
        print("=" * 80)

        raise InvalidResponseError(
            "Roadmap schema validation failed."
        ) from e