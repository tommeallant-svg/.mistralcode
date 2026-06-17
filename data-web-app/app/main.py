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
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
import os

from .config import settings
from .api import dataset_router, health_router, auth_router, trips_router, steps_router, ai_router

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
    title="Road - Travel Management",
    version=settings.app.app_version,
    description="""
    Road - Travel trip management application with AI assistant
    
    ## Features
    
    * **User Authentication**: Login with username/password (demo: Paloma/laBest)
    * **Trip Management**: Create, view, edit, delete, duplicate trips
    * **Step Management**: Add steps to trips with categories and GPS locations
    * **Visualization**: View trips and steps on interactive maps
    * **AI Assistant**: Get travel suggestions and add them as steps
    * **Responsive Design**: Works on mobile and desktop
    
    ## Models
    
    - **Trip**: name, description, start_date, end_date, status (draft/validated), GPS location
    - **Step**: name, category (transport/accommodation/activity/food/sport/hobbies), type, start_datetime, end_datetime, GPS locations
    - **User**: username, password, email, full_name
    
    ## API Endpoints
    
    ### Authentication
    - POST /api/v1/auth/login - Login with username/password
    - GET /api/v1/auth/me - Get current user
    - POST /api/v1/auth/logout - Logout
    
    ### Trips
    - GET /api/v1/trips/ - List all trips
    - POST /api/v1/trips/ - Create a trip
    - GET /api/v1/trips/{id} - Get trip details
    - PUT /api/v1/trips/{id} - Update a trip
    - DELETE /api/v1/trips/{id} - Delete a trip
    - POST /api/v1/trips/{id}/duplicate - Duplicate a trip
    - GET /api/v1/trips/{id}/map - Get trip map data
    
    ### Steps
    - GET /api/v1/steps/ - List steps for a trip
    - POST /api/v1/steps/ - Create a step
    - GET /api/v1/steps/{id} - Get step details
    - PUT /api/v1/steps/{id} - Update a step
    - DELETE /api/v1/steps/{id} - Delete a step
    - POST /api/v1/steps/{id}/duplicate - Duplicate a step
    - POST /api/v1/steps/reorder - Reorder steps
    
    ### AI
    - POST /api/v1/ai/chat - Chat with AI assistant
    - GET /api/v1/ai/proposals/suggestions - Get AI suggestions
    """,
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
app.include_router(auth_router)
app.include_router(trips_router)
app.include_router(steps_router)
app.include_router(ai_router)


# Root endpoint - Serve the SPA index.html for all non-API routes
@app.get("/", response_class=HTMLResponse, tags=["root"])
async def root():
    """Root endpoint - serves the SPA"""
    return FileResponse("static/index.html")


# Catch-all for client-side routing (for SPA navigation)
@app.get("/{path:path}", response_class=HTMLResponse)
async def serve_spa(path: str):
    """Serve index.html for all non-API routes to support SPA routing"""
    # Don't serve index.html for API routes or static files
    if path.startswith("api/") or path.startswith("docs") or path.startswith("openapi.json") or path.startswith("redoc"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Check if the file exists in static directory
    static_path = os.path.join("static", path)
    if os.path.exists(static_path) and os.path.isfile(static_path):
        return FileResponse(static_path)
    
    # For SPA routing, serve index.html
    return FileResponse("static/index.html")


from fastapi import HTTPException


# Serve favicon.ico
@app.get("/favicon.ico")
async def favicon():
    """Serve favicon.ico or return 204 if not found"""
    favicon_path = "static/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    # Return empty response to avoid 404 error
    return HTMLResponse(content="", status_code=204)


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
