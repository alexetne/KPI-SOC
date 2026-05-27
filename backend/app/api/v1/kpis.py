from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.dynamic_table import DynamicRow
from app.schemas.kpi import KpiDefinition, KpiQuery, KpiResult
from app.services.kpi_engine import apply_filters, compute_kpi, list_kpi_definitions

router = APIRouter()


@router.get("/definitions", response_model=list[KpiDefinition])
def definitions() -> list[KpiDefinition]:
    return list_kpi_definitions()


@router.post("/query", response_model=KpiResult)
def query_kpi(payload: KpiQuery, db: Session = Depends(get_db)) -> KpiResult:
    rows = list(db.scalars(select(DynamicRow).where(DynamicRow.table_id == payload.table_id)).all())
    values = apply_filters([row.values for row in rows], payload.filters)
    try:
        return compute_kpi(payload.metric_key, values, payload.mapping)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
