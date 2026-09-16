"""
Trip API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from datetime import datetime
import logging

from ..schemas.trip import (
    TripResponse, TripListResponse, TripSummaryResponse, TripTableRow, 
    TripCreate, TripUpdate
)
from ..schemas.step import StepResponse, StepTableRow
from ..schemas.user import MessageResponse
from ..services.trip_service import TripService
from ..services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/trips", tags=["trips"])

logger = logging.getLogger(__name__)

security = HTTPBearer()


def get_trip_service():
    """Dependency for getting trip service"""
    return TripService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from token"""
    service = AuthService()
    await service.initialize()
    try:
        token = credentials.credentials
        user = await service.get_current_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user.id
    finally:
        await service.shutdown()


@router.get("/", response_model=TripListResponse, summary="List all trips")
async def list_trips(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of trips"),
    offset: int = Query(default=0, ge=0, description="Number of trips to skip"),
    status: Optional[str] = Query(default=None, description="Filter by status (brouillon/validé)"),
    user_id: int = Depends(get_current_user),
    service: TripService = Depends(get_trip_service)
):
    """List all trips for the current user"""
    await service.initialize()
    try:
        response = await service.list_trips(user_id, limit, offset, status)
        return response
    except Exception as e:
        logger.error(f"Error listing trips: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/table", response_model=List[TripTableRow], summary="List trips for table")
async def list_trips_for_table(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = Query(default=None),
    user_id: int = Depends(get_current_user),
    service: TripService = Depends(get_trip_service)
):
    """List trips formatted for table display"""
    await service.initialize()
    try:
        return await service.list_trips_for_table(user_id, limit, offset, status)
    except Exception as e:
        logger.error(f"Error listing trips for table: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/{trip_id}", response_model=TripResponse, summary="Get a trip")
async def get_trip(
    trip_id: int,
    user_id: int = Depends(get_current_user),
    service: TripService = Depends(get_trip_service)
):
    """Get a specific trip by ID"""
    await service.initialize()
    try:
        trip = await service.get_trip(trip_id, user_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found or no access")
        return trip
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.post("/", response_model=TripResponse, summary="Create a new trip")
async def create_trip(
    trip_data: TripCreate,
    user_id: int = Depends(get_current_user),
    service: TripService = Depends(get_trip_service)
):
    """Create a new trip"""
    await service.initialize()
    try:
        return await service.create_trip(user_id, trip_data.model_dump())
    except Exception as e:
        logger.error(f"Error creating trip: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await service.shutdown()


@router.put("/{trip_id}", response_model=TripResponse, summary="Update a trip")
async def update_trip(
    trip_id: int,
    trip_data: TripUpdate,
    user_id: int = Depends(get_current_user),
    service: TripService = Depends(get_trip_service)
):
    """Update a trip"""
    await service.initialize()
    try:
        updated_trip = await service.update_trip(trip_id, user_id, trip_data.model_dump(exclude_unset=True))
        if not updated_trip:
            raise HTTPException(status_code=404, detail="Trip not found or no access")
        return updated_trip
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trip: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await service.shutdown()


@router.delete("/{trip_id}", response_model=MessageResponse, summary="Delete a trip")
async def delete_trip(
    trip_id: int,
    user_id: int = Depends(get_current_user),
    service: TripService = Depends(get_trip_service)
):
    """Delete a trip"""
    await service.initialize()
    try:
        success = await service.delete_trip(trip_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Trip not found or no access")
        return MessageResponse(message="Trip deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.post("/{trip_id}/duplicate", response_model=TripResponse, summary="Duplicate a trip")
async def duplicate_trip(
    trip_id: int,
    new_name: str = Query(..., description="Name for the duplicated trip"),
    user_id: int = Depends(get_current_user),
    service: TripService = Depends(get_trip_service)
):
    """Duplicate a trip"""
    await service.initialize()
    try:
        new_trip = await service.duplicate_trip(trip_id, user_id, new_name)
        if not new_trip:
            raise HTTPException(status_code=404, detail="Trip not found or no access")
        return new_trip
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error duplicating trip: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/{trip_id}/map", summary="Get trip map data")
async def get_trip_map_data(
    trip_id: int,
    user_id: int = Depends(get_current_user),
    service: TripService = Depends(get_trip_service)
):
    """Get data for displaying a trip on a map"""
    await service.initialize()
    try:
        map_data = await service.get_trip_map_data(trip_id, user_id)
        if not map_data:
            raise HTTPException(status_code=404, detail="Trip not found or no access")
        return map_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trip map data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/categories/colors", summary="Get category colors")
async def get_category_colors(
    service: TripService = Depends(get_trip_service)
):
    """Get color mapping for categories"""
    await service.initialize()
    try:
        return await service.get_category_colors()
    except Exception as e:
        logger.error(f"Error getting category colors: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()
