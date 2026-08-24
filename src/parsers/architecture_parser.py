import json
from typing import Any

from pydantic import ValidationError

from src.exceptions.llm_exceptions import InvalidResponseError
from src.models.architecture import ArchitectureReport


def _text(value: Any) -> str:
    """Convert a model value into safe display text."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    return json.dumps(value, ensure_ascii=False)


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _string_list(value: Any) -> list[str]:
    return [_text(item) for item in _list(value) if item is not None]


def _normalise_architecture(payload: dict[str, Any]) -> dict[str, Any]:
    """Accept small, common JSON-schema deviations from LLM providers."""
    normalised: dict[str, Any] = {
        "architecture_overview": _text(
            payload.get("architecture_overview", payload.get("overview", ""))
        ),
        "architectural_pattern": _text(
            payload.get("architectural_pattern", payload.get("pattern", ""))
        ),
        "mermaid_diagram": _text(payload.get("mermaid_diagram", "")),
    }

    components = []
    for item in _list(payload.get("components")):
        if isinstance(item, dict):
            components.append({
                "name": _text(item.get("name", item.get("component", ""))),
                "type": _text(item.get("type", item.get("layer", item.get("kind", "")))),
                "responsibility": _text(item.get("responsibility", item.get("description", item.get("purpose", "")))),
                "technology": _text(item.get("technology", item.get("tech", item.get("stack", "")))),
            })
    normalised["components"] = components

    data_flow = []
    for index, item in enumerate(_list(payload.get("data_flow", payload.get("flow"))), start=1):
        if isinstance(item, dict):
            data_flow.append({
                "step": item.get("step", index),
                "from_component": _text(item.get("from_component", item.get("from", ""))),
                "to_component": _text(item.get("to_component", item.get("to", ""))),
                "data": _text(item.get("data", item.get("description", ""))),
            })
    normalised["data_flow"] = data_flow

    api_contracts = []
    for item in _list(payload.get("api_contracts", payload.get("apis"))):
        if isinstance(item, dict):
            api_contracts.append({
                "method": _text(item.get("method", "")),
                "path": _text(item.get("path", item.get("endpoint", ""))),
                "purpose": _text(item.get("purpose", item.get("description", ""))),
                "request": _text(item.get("request", item.get("request_body", ""))),
                "response": _text(item.get("response", item.get("response_body", ""))),
            })
    normalised["api_contracts"] = api_contracts

    database_design = []
    for item in _list(payload.get("database_design", payload.get("database_entities"))):
        if isinstance(item, dict):
            database_design.append({
                "name": _text(item.get("name", item.get("entity", ""))),
                "purpose": _text(item.get("purpose", item.get("description", ""))),
                "key_fields": _string_list(item.get("key_fields", item.get("fields"))),
            })
    normalised["database_design"] = database_design

    for key in (
        "authentication_and_security",
        "scalability",
        "deployment",
        "folder_structure",
        "implementation_order",
        "key_architecture_decisions",
    ):
        normalised[key] = _string_list(payload.get(key))

    return normalised


def parse_architecture(response: str) -> ArchitectureReport:
    try:
        from src.parsers.utils import extract_json
        text = extract_json(response)
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise InvalidResponseError("Architecture response must be a JSON object.")

        return ArchitectureReport.model_validate(_normalise_architecture(payload))
    except json.JSONDecodeError as exc:
        raise InvalidResponseError("Gemini returned invalid architecture JSON.") from exc
    except ValidationError as exc:
        raise InvalidResponseError("Architecture schema validation failed.") from exc
