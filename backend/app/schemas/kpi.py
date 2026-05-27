from typing import Any, Literal

from pydantic import BaseModel

ChartType = Literal["stat", "bar", "line", "pie", "table"]


class KpiDefinition(BaseModel):
    key: str
    label: str
    description: str
    chart_type: ChartType
    required_columns: list[str]


class KpiQuery(BaseModel):
    table_id: str
    metric_key: str
    mapping: dict[str, str]
    filters: dict[str, Any] = {}


class KpiResult(BaseModel):
    metric_key: str
    label: str
    chart_type: ChartType
    value: Any
    series: list[dict[str, Any]] = []
