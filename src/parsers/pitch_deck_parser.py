import json

from pydantic import ValidationError

from src.exceptions.llm_exceptions import InvalidResponseError
from src.models.pitch_deck import PitchDeck


def parse_pitch_deck(response: str) -> PitchDeck:
    """
    Parse Gemini response into a validated PitchDeck model.
    """

    try:

        from src.parsers.utils import extract_json
        text = extract_json(response)
        data = json.loads(text)

        return PitchDeck.model_validate(data)

    except json.JSONDecodeError as e:

        raise InvalidResponseError(
            "Gemini returned invalid JSON."
        ) from e

    except ValidationError as e:

        raise InvalidResponseError(
            "Pitch deck schema validation failed."
        ) from e