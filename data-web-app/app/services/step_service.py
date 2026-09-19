"""
Step service for business logic related to steps.
"""

import logging
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..config import settings
from ..models.step import Step, StepCategory, TransportType
from ..models.trip import Trip
from ..schemas.step import (
    StepResponse, StepListResponse, StepTableRow, StepReorderRequest
)
from ..repositories.step_repository import StepRepository
from ..repositories.trip_repository import TripRepository

logger = logging.getLogger(__name__)


class StepService:
    """Service for step operations"""
    
    def __init__(self):
        self.engine = None
        self.session_maker = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the service with database connection"""
        if self._initialized:
            return
        
        database_url = settings.database.database_url
        
        self.engine = create_async_engine(
            database_url,
            pool_size=settings.database.db_pool_size,
            max_overflow=settings.database.db_max_overflow,
            echo=False
        )
        self.session_maker = sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        self._initialized = True
    
    async def shutdown(self):
        """Shutdown the service"""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_maker = None
            self._initialized = False
    
    async def _get_session(self) -> AsyncSession:
        """Get a database session"""
        await self.initialize()
        return self.session_maker()
    
    async def get_step(self, step_id: int, user_id: int) -> Optional[StepResponse]:
        """Get a step by ID with access check"""
        async with await self._get_session() as session:
            repo = StepRepository(session)
            step = await repo.get_by_id_with_access_check(step_id, user_id)
            
            if not step:
                return None
            
            return StepResponse(
                id=step.id,
                name=step.name,
                category=step.category,
                type=step.type,
                start_datetime=step.start_datetime,
                end_datetime=step.end_datetime,
                location_start=step.location_start,
                location_end=step.location_end,
                latitude_start=step.latitude_start,
                longitude_start=step.longitude_start,
                latitude_end=step.latitude_end,
                longitude_end=step.longitude_end,
                notes=step.notes,
                order_index=step.order_index,
                color=step.color,
                trip_id=step.trip_id,
                created_at=step.created_at,
                updated_at=step.updated_at
            )
    
    async def list_steps(self, trip_id: int, user_id: int, 
                         category_filter: Optional[str] = None) -> StepListResponse:
        """List steps for a trip"""
        async with await self._get_session() as session:
            repo = StepRepository(session)
            steps = await repo.list_by_trip(trip_id, category_filter, user_id)
            
            step_responses = [
                StepResponse(
                    id=s.id,
                    name=s.name,
                    category=s.category,
                    type=s.type,
                    start_datetime=s.start_datetime,
                    end_datetime=s.end_datetime,
                    location_start=s.location_start,
                    location_end=s.location_end,
                    latitude_start=s.latitude_start,
                    longitude_start=s.longitude_start,
                    latitude_end=s.latitude_end,
                    longitude_end=s.longitude_end,
                    notes=s.notes,
                    order_index=s.order_index,
                    color=s.color,
                    trip_id=s.trip_id,
                    created_at=s.created_at,
                    updated_at=s.updated_at
                )
                for s in steps
            ]
            
            return StepListResponse(
                steps=step_responses,
                total=len(step_responses),
                trip_id=trip_id
            )
    
    async def list_steps_for_table(self, trip_id: int, user_id: int,
                                    category_filter: Optional[str] = None) -> List[StepTableRow]:
        """List steps formatted for table display"""
        async with await self._get_session() as session:
            repo = StepRepository(session)
            steps = await repo.list_by_trip(trip_id, category_filter, user_id)
            
            return [
                StepTableRow(
                    id=s.id,
                    name=s.name,
                    category=s.category,
                    type=s.type,
                    start_datetime=s.start_datetime,
                    end_datetime=s.end_datetime,
                    location_start=s.location_start,
                    location_end=s.location_end,
                    order_index=s.order_index,
                    color=s.color
                )
                for s in steps
            ]
    
    async def create_step(self, user_id: int, step_data: dict) -> Optional[StepResponse]:
        """Create a new step"""
        async with await self._get_session() as session:
            # Verify user has access to the trip
            trip_repo = TripRepository(session)
            trip = await trip_repo.get_by_id_with_access_check(step_data["trip_id"], user_id)
            if not trip:
                return None
            
            # Convert category string (no longer using enum)
            category = step_data.get("category", "activité")
            if category not in ["transport", "hébergement", "activité", "food", "sport", "hobbies"]:
                category = "activité"
            step_data["category"] = category
            
            # Set color based on category if not provided
            if "color" not in step_data or not step_data["color"]:
                colors = await self.get_colors_by_category()
                step_data["color"] = colors.get(category, "#666666")
            
            # Set order_index to the next available
            step_repo = StepRepository(session)
            existing_steps = await step_repo.list_by_trip(step_data["trip_id"])
            step_data["order_index"] = len(existing_steps)
            
            step = await step_repo.create(step_data)
            
            return StepResponse(
                id=step.id,
                name=step.name,
                category=step.category,
                type=step.type,
                start_datetime=step.start_datetime,
                end_datetime=step.end_datetime,
                location_start=step.location_start,
                location_end=step.location_end,
                latitude_start=step.latitude_start,
                longitude_start=step.longitude_start,
                latitude_end=step.latitude_end,
                longitude_end=step.longitude_end,
                notes=step.notes,
                order_index=step.order_index,
                color=step.color,
                trip_id=step.trip_id,
                created_at=step.created_at,
                updated_at=step.updated_at
            )
    
    async def update_step(self, step_id: int, user_id: int, update_data: dict) -> Optional[StepResponse]:
        """Update a step"""
        async with await self._get_session() as session:
            repo = StepRepository(session)
            
            # Convert category string if provided
            if "category" in update_data:
                category = update_data["category"]
                if category not in ["transport", "hébergement", "activité", "food", "sport", "hobbies"]:
                    update_data["category"] = "activité"
            
            step = await repo.update(step_id, update_data, user_id)
            
            if not step:
                return None
            
            return StepResponse(
                id=step.id,
                name=step.name,
                category=step.category,
                type=step.type,
                start_datetime=step.start_datetime,
                end_datetime=step.end_datetime,
                location_start=step.location_start,
                location_end=step.location_end,
                latitude_start=step.latitude_start,
                longitude_start=step.longitude_start,
                latitude_end=step.latitude_end,
                longitude_end=step.longitude_end,
                notes=step.notes,
                order_index=step.order_index,
                color=step.color,
                trip_id=step.trip_id,
                created_at=step.created_at,
                updated_at=step.updated_at
            )
    
    async def delete_step(self, step_id: int, user_id: int) -> bool:
        """Delete a step"""
        async with await self._get_session() as session:
            repo = StepRepository(session)
            return await repo.delete(step_id, user_id)
    
    async def duplicate_step(self, step_id: int, user_id: int) -> Optional[StepResponse]:
        """Duplicate a step"""
        async with await self._get_session() as session:
            repo = StepRepository(session)
            new_step = await repo.duplicate(step_id, user_id)
            
            if not new_step:
                return None
            
            return StepResponse(
                id=new_step.id,
                name=new_step.name,
                category=new_step.category,
                type=new_step.type,
                start_datetime=new_step.start_datetime,
                end_datetime=new_step.end_datetime,
                location_start=new_step.location_start,
                location_end=new_step.location_end,
                latitude_start=new_step.latitude_start,
                longitude_start=new_step.longitude_start,
                latitude_end=new_step.latitude_end,
                longitude_end=new_step.longitude_end,
                notes=new_step.notes,
                order_index=new_step.order_index,
                color=new_step.color,
                trip_id=new_step.trip_id,
                created_at=new_step.created_at,
                updated_at=new_step.updated_at
            )
    
    async def reorder_steps(self, trip_id: int, user_id: int, 
                           request: StepReorderRequest) -> bool:
        """Reorder steps in a trip"""
        async with await self._get_session() as session:
            repo = StepRepository(session)
            return await repo.set_steps_order(trip_id, request.step_ids, user_id)
    
    async def get_categories(self) -> List[str]:
        """Get all available categories"""
        async with await self._get_session() as session:
            repo = StepRepository(session)
            return await repo.get_categories()
    
    async def get_transport_types(self) -> List[str]:
        """Get all available transport types"""
        async with await self._get_session() as session:
            repo = StepRepository(session)
            return await repo.get_transport_types()
    
    async def get_colors_by_category(self) -> Dict[str, str]:
        """Get default colors for each category"""
        return {
            "transport": "#3B82F6",
            "hébergement": "#10B981",
            "activité": "#F59E0B",
            "food": "#EF4444",
            "sport": "#8B5CF6",
            "hobbies": "#EC4899"
        }
