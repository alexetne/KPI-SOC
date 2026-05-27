from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.dynamic_table import DynamicColumn, DynamicRow, DynamicTable
from app.schemas.dynamic_table import (
    DynamicColumnCreate,
    DynamicColumnPatch,
    DynamicColumnRead,
    DynamicRowCreate,
    DynamicRowPatch,
    DynamicRowRead,
    DynamicTableCreate,
    DynamicTablePatch,
    DynamicTableRead,
)
from app.services.table_validation import validate_row_values

router = APIRouter()


@router.get("", response_model=list[DynamicTableRead])
def list_tables(db: Session = Depends(get_db)) -> list[DynamicTable]:
    statement = select(DynamicTable).options(selectinload(DynamicTable.columns)).order_by(DynamicTable.name)
    return list(db.scalars(statement).all())


@router.post("", response_model=DynamicTableRead, status_code=status.HTTP_201_CREATED)
def create_table(payload: DynamicTableCreate, db: Session = Depends(get_db)) -> DynamicTable:
    table = DynamicTable(**payload.model_dump())
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


@router.patch("/{table_id}", response_model=DynamicTableRead)
def patch_table(table_id: str, payload: DynamicTablePatch, db: Session = Depends(get_db)) -> DynamicTable:
    table = db.scalar(
        select(DynamicTable).where(DynamicTable.id == table_id).options(selectinload(DynamicTable.columns))
    )
    if table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(table, key, value)
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(table_id: str, db: Session = Depends(get_db)) -> None:
    table = db.get(DynamicTable, table_id)
    if table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    db.delete(table)
    db.commit()


@router.get("/{table_id}", response_model=DynamicTableRead)
def get_table(table_id: str, db: Session = Depends(get_db)) -> DynamicTable:
    table = db.scalar(
        select(DynamicTable).where(DynamicTable.id == table_id).options(selectinload(DynamicTable.columns))
    )
    if table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    return table


@router.post("/{table_id}/columns", response_model=DynamicColumnRead, status_code=status.HTTP_201_CREATED)
def create_column(
    table_id: str, payload: DynamicColumnCreate, db: Session = Depends(get_db)
) -> DynamicColumn:
    table = db.get(DynamicTable, table_id)
    if table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    column = DynamicColumn(table_id=table_id, **payload.model_dump())
    db.add(column)
    db.commit()
    db.refresh(column)
    return column


@router.patch("/{table_id}/columns/{column_id}", response_model=DynamicColumnRead)
def patch_column(
    table_id: str, column_id: str, payload: DynamicColumnPatch, db: Session = Depends(get_db)
) -> DynamicColumn:
    column = db.scalar(
        select(DynamicColumn).where(DynamicColumn.table_id == table_id, DynamicColumn.id == column_id)
    )
    if column is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(column, key, value)
    db.add(column)
    db.commit()
    db.refresh(column)
    return column


@router.delete("/{table_id}/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_column(table_id: str, column_id: str, db: Session = Depends(get_db)) -> None:
    column = db.scalar(
        select(DynamicColumn).where(DynamicColumn.table_id == table_id, DynamicColumn.id == column_id)
    )
    if column is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")
    rows = db.scalars(select(DynamicRow).where(DynamicRow.table_id == table_id)).all()
    for row in rows:
        if column.key in row.values:
            values = dict(row.values)
            values.pop(column.key, None)
            row.values = values
            db.add(row)
    db.delete(column)
    db.commit()


@router.get("/{table_id}/rows", response_model=list[DynamicRowRead])
def list_rows(
    table_id: str,
    q: str | None = None,
    column: str | None = None,
    value: str | None = None,
    limit: int = 200,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[DynamicRow]:
    statement = select(DynamicRow).where(DynamicRow.table_id == table_id).order_by(DynamicRow.created_at.desc())
    rows = list(db.scalars(statement).all())
    if q:
        needle = q.lower()
        rows = [row for row in rows if needle in " ".join(str(item).lower() for item in row.values.values())]
    if column and value is not None:
        rows = [row for row in rows if str(row.values.get(column, "")).lower() == value.lower()]
    return rows[offset : offset + min(limit, 1000)]


@router.post("/{table_id}/rows", response_model=DynamicRowRead, status_code=status.HTTP_201_CREATED)
def create_row(table_id: str, payload: DynamicRowCreate, db: Session = Depends(get_db)) -> DynamicRow:
    table = db.scalar(
        select(DynamicTable).where(DynamicTable.id == table_id).options(selectinload(DynamicTable.columns))
    )
    if table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    values = validate_row_values(table.columns, payload.values)
    row = DynamicRow(table_id=table_id, values=values)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.patch("/{table_id}/rows/{row_id}", response_model=DynamicRowRead)
def patch_row(table_id: str, row_id: str, payload: DynamicRowPatch, db: Session = Depends(get_db)) -> DynamicRow:
    table = db.scalar(
        select(DynamicTable).where(DynamicTable.id == table_id).options(selectinload(DynamicTable.columns))
    )
    row = db.scalar(select(DynamicRow).where(DynamicRow.table_id == table_id, DynamicRow.id == row_id))
    if table is None or row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Row not found")
    values = {**row.values, **payload.values}
    row.values = validate_row_values(table.columns, values)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{table_id}/rows/{row_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_row(table_id: str, row_id: str, db: Session = Depends(get_db)) -> None:
    row = db.scalar(select(DynamicRow).where(DynamicRow.table_id == table_id, DynamicRow.id == row_id))
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Row not found")
    db.delete(row)
    db.commit()
