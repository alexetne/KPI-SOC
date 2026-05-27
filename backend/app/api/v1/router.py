from fastapi import APIRouter

from app.api.v1 import dashboards, demo, health, integrations, kpis, tables

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(tables.router, prefix="/tables", tags=["tables"])
api_router.include_router(kpis.router, prefix="/kpis", tags=["kpis"])
api_router.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
