from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDTimestampMixin


class Dashboard(UUIDTimestampMixin, Base):
    __tablename__ = "dashboards"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    panels: Mapped[list["DashboardPanel"]] = relationship(
        back_populates="dashboard", cascade="all, delete-orphan", order_by="DashboardPanel.position"
    )


class DashboardPanel(UUIDTimestampMixin, Base):
    __tablename__ = "dashboard_panels"

    dashboard_id: Mapped[str] = mapped_column(ForeignKey("dashboards.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    panel_type: Mapped[str] = mapped_column(String(40))
    metric_key: Mapped[str] = mapped_column(String(120))
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    position: Mapped[int] = mapped_column(Integer, default=0)

    dashboard: Mapped[Dashboard] = relationship(back_populates="panels")
