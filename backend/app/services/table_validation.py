from typing import Any

from fastapi import HTTPException, status

from app.models.dynamic_table import DynamicColumn


def validate_row_values(columns: list[DynamicColumn], values: dict[str, Any]) -> dict[str, Any]:
    known_columns = {column.key: column for column in columns}
    unknown = set(values) - set(known_columns)
    if unknown:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown columns: {', '.join(sorted(unknown))}",
        )

    missing = [column.key for column in columns if column.required and column.key not in values]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing required columns: {', '.join(missing)}",
        )

    for key, value in values.items():
        column = known_columns[key]
        if value is None:
            continue
        _validate_value_type(column, value)

    return values


def _validate_value_type(column: DynamicColumn, value: Any) -> None:
    valid = True

    if column.data_type in {"text", "severity", "endpoint", "status", "date", "datetime"}:
        valid = isinstance(value, str)
    elif column.data_type == "number":
        valid = isinstance(value, int | float) and not isinstance(value, bool)
    elif column.data_type == "boolean":
        valid = isinstance(value, bool)
    elif column.data_type == "enum":
        choices = (column.options or {}).get("choices", [])
        valid = isinstance(value, str) and (not choices or value in choices)

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid value for column '{column.key}' of type '{column.data_type}'",
        )
