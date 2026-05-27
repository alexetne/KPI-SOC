from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.dynamic_table import DynamicTable
from app.schemas.dynamic_table import DynamicTableRead
from app.services.demo_seed import seed_security_alerts

router = APIRouter()


@router.post("/seed", response_model=DynamicTableRead, status_code=status.HTTP_201_CREATED)
def seed_demo(db: Session = Depends(get_db)) -> DynamicTable:
    return seed_security_alerts(db)
