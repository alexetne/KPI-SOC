from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class DashboardPanelCreate(BaseModel):
    title: str
    panel_type: str
    metric_key: str
    config: dict[str, Any] = {}
    position: int = 0


class DashboardPanelRead(DashboardPanelCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dashboard_id: str
    created_at: datetime
    updated_at: datetime


class DashboardCreate(BaseModel):
    name: str
    label: str
    description: str | None = None


class DashboardRead(DashboardCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    panels: list[DashboardPanelRead] = []
