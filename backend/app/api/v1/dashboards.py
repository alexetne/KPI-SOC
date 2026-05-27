from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.dashboard import Dashboard, DashboardPanel
from app.schemas.dashboard import DashboardCreate, DashboardPanelCreate, DashboardPanelRead, DashboardRead

router = APIRouter()


@router.get("", response_model=list[DashboardRead])
def list_dashboards(db: Session = Depends(get_db)) -> list[Dashboard]:
    statement = select(Dashboard).options(selectinload(Dashboard.panels)).order_by(Dashboard.name)
    return list(db.scalars(statement).all())


@router.post("", response_model=DashboardRead, status_code=status.HTTP_201_CREATED)
def create_dashboard(payload: DashboardCreate, db: Session = Depends(get_db)) -> Dashboard:
    dashboard = Dashboard(**payload.model_dump())
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    return dashboard


@router.post("/{dashboard_id}/panels", response_model=DashboardPanelRead, status_code=status.HTTP_201_CREATED)
def create_panel(
    dashboard_id: str, payload: DashboardPanelCreate, db: Session = Depends(get_db)
) -> DashboardPanel:
    dashboard = db.get(Dashboard, dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    panel = DashboardPanel(dashboard_id=dashboard_id, **payload.model_dump())
    db.add(panel)
    db.commit()
    db.refresh(panel)
    return panel
