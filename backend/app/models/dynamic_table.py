from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDTimestampMixin


class DynamicTable(UUIDTimestampMixin, Base):
    __tablename__ = "dynamic_tables"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    columns: Mapped[list["DynamicColumn"]] = relationship(
        back_populates="table", cascade="all, delete-orphan", order_by="DynamicColumn.position"
    )
    rows: Mapped[list["DynamicRow"]] = relationship(back_populates="table", cascade="all, delete-orphan")


class DynamicColumn(UUIDTimestampMixin, Base):
    __tablename__ = "dynamic_columns"
    __table_args__ = (UniqueConstraint("table_id", "key", name="uq_dynamic_column_table_key"),)

    table_id: Mapped[str] = mapped_column(ForeignKey("dynamic_tables.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(120), index=True)
    label: Mapped[str] = mapped_column(String(160))
    data_type: Mapped[str] = mapped_column(String(40))
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0)

    table: Mapped[DynamicTable] = relationship(back_populates="columns")


class DynamicRow(UUIDTimestampMixin, Base):
    __tablename__ = "dynamic_rows"

    table_id: Mapped[str] = mapped_column(ForeignKey("dynamic_tables.id", ondelete="CASCADE"), index=True)
    values: Mapped[dict] = mapped_column(JSONB, default=dict)

    table: Mapped[DynamicTable] = relationship(back_populates="rows")
