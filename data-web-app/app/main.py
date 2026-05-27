"""
Main application entry point.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from .config import settings
from .api import dataset_router, health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.app.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    # Startup
    logger.info(f"Starting {settings.app.app_name} v{settings.app.app_version}")
    logger.info(f"Data source: {settings.app.data_source}")
    logger.info(f"Debug mode: {settings.app.debug}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.app.app_name,
    version=settings.app.app_version,
    description="Web application for data manipulation with CSV and PostgreSQL support",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (for potential frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(health_router)
app.include_router(dataset_router)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "name": settings.app.app_name,
        "version": settings.app.app_version,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


# Error handlers
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug,
        log_level="debug" if settings.app.debug else "info"
    )
