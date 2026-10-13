from fastapi import APIRouter

from app.api.routes import analysis, holdings, reports

api_router = APIRouter()
api_router.include_router(holdings.router, prefix="/holdings", tags=["holdings"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
