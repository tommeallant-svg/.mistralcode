"""
Step API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import logging

from ..schemas.step import (
    StepResponse, StepListResponse, StepTableRow, StepCreate, StepUpdate,
    StepReorderRequest
)
from ..schemas.user import MessageResponse
from ..services.step_service import StepService
from ..services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/steps", tags=["steps"])

logger = logging.getLogger(__name__)

security = HTTPBearer()


def get_step_service():
    """Dependency for getting step service"""
    return StepService()


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


@router.get("/", response_model=StepListResponse, summary="List all steps for a trip")
async def list_steps(
    trip_id: int = Query(..., description="Trip ID"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    user_id: int = Depends(get_current_user),
    service: StepService = Depends(get_step_service)
):
    """List all steps for a specific trip"""
    await service.initialize()
    try:
        response = await service.list_steps(trip_id, user_id, category)
        return response
    except Exception as e:
        logger.error(f"Error listing steps: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/table", response_model=List[StepTableRow], summary="List steps for table")
async def list_steps_for_table(
    trip_id: int = Query(..., description="Trip ID"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    user_id: int = Depends(get_current_user),
    service: StepService = Depends(get_step_service)
):
    """List steps formatted for table display"""
    await service.initialize()
    try:
        return await service.list_steps_for_table(trip_id, user_id, category)
    except Exception as e:
        logger.error(f"Error listing steps for table: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/{step_id}", response_model=StepResponse, summary="Get a step")
async def get_step(
    step_id: int,
    user_id: int = Depends(get_current_user),
    service: StepService = Depends(get_step_service)
):
    """Get a specific step by ID"""
    await service.initialize()
    try:
        step = await service.get_step(step_id, user_id)
        if not step:
            raise HTTPException(status_code=404, detail="Step not found or no access")
        return step
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting step: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.post("/", response_model=StepResponse, summary="Create a new step")
async def create_step(
    step_data: StepCreate,
    user_id: int = Depends(get_current_user),
    service: StepService = Depends(get_step_service)
):
    """Create a new step"""
    await service.initialize()
    try:
        step = await service.create_step(user_id, step_data.model_dump())
        if not step:
            raise HTTPException(status_code=404, detail="Trip not found or no access")
        return step
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating step: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await service.shutdown()


@router.put("/{step_id}", response_model=StepResponse, summary="Update a step")
async def update_step(
    step_id: int,
    step_data: StepUpdate,
    user_id: int = Depends(get_current_user),
    service: StepService = Depends(get_step_service)
):
    """Update a step"""
    await service.initialize()
    try:
        updated_step = await service.update_step(step_id, user_id, step_data.model_dump(exclude_unset=True))
        if not updated_step:
            raise HTTPException(status_code=404, detail="Step not found or no access")
        return updated_step
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating step: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await service.shutdown()


@router.delete("/{step_id}", response_model=MessageResponse, summary="Delete a step")
async def delete_step(
    step_id: int,
    user_id: int = Depends(get_current_user),
    service: StepService = Depends(get_step_service)
):
    """Delete a step"""
    await service.initialize()
    try:
        success = await service.delete_step(step_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Step not found or no access")
        return MessageResponse(message="Step deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting step: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.post("/{step_id}/duplicate", response_model=StepResponse, summary="Duplicate a step")
async def duplicate_step(
    step_id: int,
    user_id: int = Depends(get_current_user),
    service: StepService = Depends(get_step_service)
):
    """Duplicate a step"""
    await service.initialize()
    try:
        new_step = await service.duplicate_step(step_id, user_id)
        if not new_step:
            raise HTTPException(status_code=404, detail="Step not found or no access")
        return new_step
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error duplicating step: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await service.shutdown()


@router.post("/reorder", response_model=MessageResponse, summary="Reorder steps")
async def reorder_steps(
    request: StepReorderRequest,
    user_id: int = Depends(get_current_user),
    service: StepService = Depends(get_step_service)
):
    """Reorder steps in a trip"""
    await service.initialize()
    try:
        success = await service.reorder_steps(request.trip_id, user_id, request)
        if not success:
            raise HTTPException(status_code=404, detail="Trip not found or no access")
        return MessageResponse(message="Steps reordered successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering steps: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/categories", summary="Get all categories")
async def get_categories(
    service: StepService = Depends(get_step_service)
):
    """Get all available categories for steps"""
    await service.initialize()
    try:
        return await service.get_categories()
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/transport-types", summary="Get all transport types")
async def get_transport_types(
    service: StepService = Depends(get_step_service)
):
    """Get all available transport types"""
    await service.initialize()
    try:
        return await service.get_transport_types()
    except Exception as e:
        logger.error(f"Error getting transport types: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/colors", summary="Get category colors")
async def get_category_colors(
    service: StepService = Depends(get_step_service)
):
    """Get default colors for each category"""
    await service.initialize()
    try:
        return await service.get_colors_by_category()
    except Exception as e:
        logger.error(f"Error getting category colors: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()
