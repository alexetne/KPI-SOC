from datetime import UTC, datetime
from typing import Any


def get_path_value(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if current is None:
            return None
        if isinstance(current, list):
            current = current[int(part)] if part.isdigit() and int(part) < len(current) else None
            continue
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def normalize_value(value: Any, data_type: str) -> Any:
    if value is None:
        return None
    if data_type == "number":
        return float(value)
    if data_type == "boolean":
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"true", "1", "yes", "oui"}
    if data_type in {"datetime", "date"}:
        if isinstance(value, int | float):
            return datetime.fromtimestamp(value, tz=UTC).isoformat()
        return str(value)
    if isinstance(value, dict):
        return value.get("name") or value.get("value") or value.get("display") or str(value)
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)
