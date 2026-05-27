"""initial schema

Revision ID: 202605270001
Revises:
Create Date: 2026-05-27
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "202605270001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "dashboards",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dashboards_name"), "dashboards", ["name"], unique=True)

    op.create_table(
        "dynamic_tables",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dynamic_tables_name"), "dynamic_tables", ["name"], unique=True)

    op.create_table(
        "dashboard_panels",
        sa.Column("dashboard_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("panel_type", sa.String(length=40), nullable=False),
        sa.Column("metric_key", sa.String(length=120), nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["dashboard_id"], ["dashboards.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dashboard_panels_dashboard_id"), "dashboard_panels", ["dashboard_id"])

    op.create_table(
        "dynamic_columns",
        sa.Column("table_id", sa.String(length=36), nullable=False),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("data_type", sa.String(length=40), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False),
        sa.Column("options", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["table_id"], ["dynamic_tables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("table_id", "key", name="uq_dynamic_column_table_key"),
    )
    op.create_index(op.f("ix_dynamic_columns_key"), "dynamic_columns", ["key"])
    op.create_index(op.f("ix_dynamic_columns_table_id"), "dynamic_columns", ["table_id"])

    op.create_table(
        "dynamic_rows",
        sa.Column("table_id", sa.String(length=36), nullable=False),
        sa.Column("values", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["table_id"], ["dynamic_tables.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dynamic_rows_table_id"), "dynamic_rows", ["table_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_dynamic_rows_table_id"), table_name="dynamic_rows")
    op.drop_table("dynamic_rows")
    op.drop_index(op.f("ix_dynamic_columns_table_id"), table_name="dynamic_columns")
    op.drop_index(op.f("ix_dynamic_columns_key"), table_name="dynamic_columns")
    op.drop_table("dynamic_columns")
    op.drop_index(op.f("ix_dashboard_panels_dashboard_id"), table_name="dashboard_panels")
    op.drop_table("dashboard_panels")
    op.drop_index(op.f("ix_dynamic_tables_name"), table_name="dynamic_tables")
    op.drop_table("dynamic_tables")
    op.drop_index(op.f("ix_dashboards_name"), table_name="dashboards")
    op.drop_table("dashboards")
