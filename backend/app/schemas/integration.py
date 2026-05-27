from typing import Any

from pydantic import BaseModel, Field


class SekoiaImportRequest(BaseModel):
    table_id: str
    api_key: str = Field(min_length=1)
    base_url: str = "https://api.sekoia.io"
    limit: int = Field(default=50, ge=1, le=500)
    query_params: dict[str, str] = {}
    mapping: dict[str, str]


class SekoiaImportResponse(BaseModel):
    imported: int
    skipped: int
    endpoint: str
    sample: list[dict[str, Any]] = []
