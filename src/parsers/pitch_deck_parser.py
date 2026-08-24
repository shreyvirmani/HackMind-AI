import json

from pydantic import ValidationError

from src.exceptions.llm_exceptions import InvalidResponseError
from src.models.pitch_deck import PitchDeck


def parse_pitch_deck(response: str) -> PitchDeck:
    """
    Parse Gemini response into a validated PitchDeck model.
    """

    try:

        response = response.strip()

        if response.startswith("```json"):
            response = response.replace("```json", "", 1)

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        data = json.loads(response)

        return PitchDeck.model_validate(data)

    except json.JSONDecodeError as e:

        raise InvalidResponseError(
            "Gemini returned invalid JSON."
        ) from e

    except ValidationError as e:

        raise InvalidResponseError(
            "Pitch deck schema validation failed."
        ) from e