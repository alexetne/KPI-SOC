from fastapi import APIRouter, Depends, HTTPException, status
from httpx import HTTPError
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.dynamic_table import DynamicRow, DynamicTable
from app.schemas.integration import SekoiaImportRequest, SekoiaImportResponse
from app.services.path_mapping import get_path_value, normalize_value
from app.services.sekoia_client import fetch_sekoia_alerts
from app.services.table_validation import validate_row_values

router = APIRouter()


@router.post("/sekoia/import-alerts", response_model=SekoiaImportResponse)
async def import_sekoia_alerts(
    payload: SekoiaImportRequest, db: Session = Depends(get_db)
) -> SekoiaImportResponse:
    table = db.scalar(
        select(DynamicTable)
        .where(DynamicTable.id == payload.table_id)
        .options(selectinload(DynamicTable.columns))
    )
    if table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    try:
        endpoint, alerts = await fetch_sekoia_alerts(
            payload.base_url,
            payload.api_key,
            payload.limit,
            payload.query_params,
        )
    except HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Sekoia request failed: {exc}",
        ) from exc

    imported = 0
    skipped = 0
    columns_by_key = {column.key: column for column in table.columns}
    samples: list[dict] = []

    for alert in alerts:
        values = {}
        for target_column, source_path in payload.mapping.items():
            column = columns_by_key.get(target_column)
            if column is None or not source_path:
                continue
            raw_value = get_path_value(alert, source_path)
            normalized = normalize_value(raw_value, column.data_type)
            if normalized is not None:
                values[target_column] = normalized
        if not values:
            skipped += 1
            continue
        row = DynamicRow(table_id=table.id, values=validate_row_values(table.columns, values))
        db.add(row)
        imported += 1
        if len(samples) < 3:
            samples.append(values)

    db.commit()
    return SekoiaImportResponse(imported=imported, skipped=skipped, endpoint=endpoint, sample=samples)
