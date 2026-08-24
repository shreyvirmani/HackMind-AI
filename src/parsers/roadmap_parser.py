import json
import re

from pydantic import ValidationError

from src.models.roadmap import Roadmap
from src.exceptions.llm_exceptions import InvalidResponseError


def _extract_json(text: str) -> str:
    """
    Extract the first JSON object from an LLM response.
    Works with Gemini, OpenAI, Claude and Groq.
    """

    text = text.strip()

    # Remove markdown fences
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()

    # Already valid JSON
    if text.startswith("{") and text.endswith("}"):
        return text

    # Extract first {...} block
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]

    raise InvalidResponseError(
        "No JSON object found in model response."
    )


def parse_roadmap(response: str) -> Roadmap:
    """
    Parse roadmap returned by any LLM.
    """

    try:

        cleaned = _extract_json(response)

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