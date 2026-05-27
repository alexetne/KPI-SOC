from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ColumnType = Literal["text", "number", "boolean", "date", "datetime", "enum", "severity", "endpoint", "status"]


class DynamicColumnBase(BaseModel):
    key: str = Field(pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$")
    label: str
    data_type: ColumnType
    required: bool = False
    options: dict[str, Any] | None = None
    position: int = 0


class DynamicColumnCreate(DynamicColumnBase):
    pass


class DynamicColumnPatch(BaseModel):
    label: str | None = None
    data_type: ColumnType | None = None
    required: bool | None = None
    options: dict[str, Any] | None = None
    position: int | None = None


class DynamicColumnRead(DynamicColumnBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    table_id: str
    created_at: datetime
    updated_at: datetime


class DynamicTableCreate(BaseModel):
    name: str = Field(pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$")
    label: str
    description: str | None = None


class DynamicTablePatch(BaseModel):
    label: str | None = None
    description: str | None = None


class DynamicTableRead(DynamicTableCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    columns: list[DynamicColumnRead] = []


class DynamicRowCreate(BaseModel):
    values: dict[str, Any]


class DynamicRowPatch(BaseModel):
    values: dict[str, Any]


class DynamicRowQuery(BaseModel):
    q: str | None = None
    column: str | None = None
    value: str | None = None
    limit: int = Field(default=200, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class DynamicRowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    table_id: str
    values: dict[str, Any]
    created_at: datetime
    updated_at: datetime
