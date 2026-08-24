import re
from src.exceptions.llm_exceptions import InvalidResponseError

def extract_json(text: str) -> str:
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
