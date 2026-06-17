"""
API routes for the application.
"""

from .datasets import router as dataset_router
from .health import router as health_router
from .auth import router as auth_router
from .trips import router as trips_router
from .steps import router as steps_router
from .ai import router as ai_router

__all__ = [
    "dataset_router",
    "health_router",
    "auth_router",
    "trips_router",
    "steps_router",
    "ai_router"
]
