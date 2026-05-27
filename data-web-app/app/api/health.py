"""
Health check API routes.
"""

from fastapi import APIRouter, Depends
from datetime import datetime

from ..schemas.dataset import HealthResponse
from ..services.dataset_service import DatasetService
from ..config import settings

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Health check endpoint")
async def health_check():
    """Check application health"""
    return HealthResponse(
        status="healthy",
        version=settings.app.app_version,
        data_source=settings.app.data_source,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@router.get("/ready", summary="Readiness check")
async def readiness_check():
    """Check if application is ready to serve requests"""
    return {"status": "ready"}


@router.get("/ping", summary="Simple ping endpoint")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}
