"""
Trip service for business logic related to trips.
"""

import logging
from typing import Optional, List, Tuple, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..config import settings
from ..models.trip import Trip, TripStatus
from ..models.step import Step, StepCategory
from ..models.user import User
from ..models.shared_trip import SharedTrip
from ..schemas.trip import (
    TripResponse, TripListResponse, TripSummaryResponse, TripTableRow
)
from ..schemas.step import StepResponse, StepTableRow
from ..repositories.trip_repository import TripRepository
from ..repositories.step_repository import StepRepository
from ..repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class TripService:
    """Service for trip operations"""
    
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
    
    async def get_trip(self, trip_id: int, user_id: int) -> Optional[TripResponse]:
        """Get a trip by ID with access check"""
        async with await self._get_session() as session:
            repo = TripRepository(session)
            trip = await repo.get_by_id_with_access_check(trip_id, user_id)
            
            if not trip:
                return None
            
            # Get steps
            step_repo = StepRepository(session)
            steps = await step_repo.list_by_trip(trip.id, user_id=user_id)
            
            return TripResponse(
                id=trip.id,
                name=trip.name,
                description=trip.description,
                start_date=trip.start_date,
                end_date=trip.end_date,
                status=trip.status,
                latitude=trip.latitude,
                longitude=trip.longitude,
                owner_id=trip.owner_id,
                owner=None,  # Can be populated if needed
                created_at=trip.created_at,
                updated_at=trip.updated_at,
                steps=[
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
                ],
                steps_count=len(steps)
            )
    
    async def list_trips(self, user_id: int, limit: int = 100, offset: int = 0,
                        status_filter: Optional[str] = None) -> TripListResponse:
        """List all trips for a user"""
        async with await self._get_session() as session:
            repo = TripRepository(session)
            trips, total = await repo.list_all_for_user(user_id, limit, offset, status_filter)
            
            trip_responses = []
            for trip in trips:
                step_repo = StepRepository(session)
                steps = await step_repo.list_by_trip(trip.id)
                
                trip_responses.append(TripSummaryResponse(
                    id=trip.id,
                    name=trip.name,
                    status=trip.status,
                    start_date=trip.start_date,
                    end_date=trip.end_date,
                    created_at=trip.created_at,
                    updated_at=trip.updated_at,
                    latitude=trip.latitude,
                    longitude=trip.longitude,
                    steps_count=len(steps)
                ))
            
            return TripListResponse(
                trips=trip_responses,
                total=total,
                limit=limit,
                offset=offset
            )
    
    async def list_trips_for_table(self, user_id: int, limit: int = 100, offset: int = 0,
                                   status_filter: Optional[str] = None) -> List[TripTableRow]:
        """List trips formatted for table display"""
        async with await self._get_session() as session:
            repo = TripRepository(session)
            trips, _ = await repo.list_all_for_user(user_id, limit, offset, status_filter)
            
            return [
                TripTableRow(
                    id=trip.id,
                    name=trip.name,
                    status=trip.status,
                    date_creation=trip.created_at,
                    date_modification=trip.updated_at
                )
                for trip in trips
            ]
    
    async def create_trip(self, user_id: int, trip_data: dict) -> TripResponse:
        """Create a new trip"""
        async with await self._get_session() as session:
            # Validate status
            status = trip_data.get("status", "brouillon")
            if status not in ["brouillon", "validé"]:
                status = "brouillon"
            
            repo = TripRepository(session)
            trip = await repo.create({
                **trip_data,
                "owner_id": user_id,
                "status": status
            })
            
            return TripResponse(
                id=trip.id,
                name=trip.name,
                description=trip.description,
                start_date=trip.start_date,
                end_date=trip.end_date,
                status=trip.status,
                latitude=trip.latitude,
                longitude=trip.longitude,
                owner_id=trip.owner_id,
                created_at=trip.created_at,
                updated_at=trip.updated_at,
                steps=[],
                steps_count=0
            )
    
    async def update_trip(self, trip_id: int, user_id: int, update_data: dict) -> Optional[TripResponse]:
        """Update a trip"""
        async with await self._get_session() as session:
            repo = TripRepository(session)
            
            # Convert status string (no longer needed as we use String directly)
            if "status" in update_data:
                status = update_data["status"]
                if status not in ["brouillon", "validé"]:
                    update_data["status"] = "brouillon"
            
            trip = await repo.update(trip_id, update_data, user_id)
            
            if not trip:
                return None
            
            # Get steps
            step_repo = StepRepository(session)
            steps = await step_repo.list_by_trip(trip.id, user_id=user_id)
            
            return TripResponse(
                id=trip.id,
                name=trip.name,
                description=trip.description,
                start_date=trip.start_date,
                end_date=trip.end_date,
                status=trip.status,
                latitude=trip.latitude,
                longitude=trip.longitude,
                owner_id=trip.owner_id,
                created_at=trip.created_at,
                updated_at=trip.updated_at,
                steps=[
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
                ],
                steps_count=len(steps)
            )
    
    async def delete_trip(self, trip_id: int, user_id: int) -> bool:
        """Delete a trip"""
        async with await self._get_session() as session:
            repo = TripRepository(session)
            return await repo.delete(trip_id, user_id)
    
    async def duplicate_trip(self, trip_id: int, user_id: int, new_name: str) -> Optional[TripResponse]:
        """Duplicate a trip"""
        async with await self._get_session() as session:
            repo = TripRepository(session)
            new_trip = await repo.duplicate(trip_id, user_id, new_name)
            
            if not new_trip:
                return None
            
            # Get steps
            step_repo = StepRepository(session)
            steps = await step_repo.list_by_trip(new_trip.id, user_id=user_id)
            
            return TripResponse(
                id=new_trip.id,
                name=new_trip.name,
                description=new_trip.description,
                start_date=new_trip.start_date,
                end_date=new_trip.end_date,
                status=new_trip.status,
                latitude=new_trip.latitude,
                longitude=new_trip.longitude,
                owner_id=new_trip.owner_id,
                created_at=new_trip.created_at,
                updated_at=new_trip.updated_at,
                steps=[
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
                ],
                steps_count=len(steps)
            )
    
    async def get_category_colors(self) -> Dict[str, str]:
        """Get color mapping for categories"""
        async with await self._get_session() as session:
            repo = TripRepository(session)
            return await repo.get_category_colors()
    
    async def get_trip_map_data(self, trip_id: int, user_id: int) -> Dict[str, Any]:
        """Get data for displaying trip on map"""
        async with await self._get_session() as session:
            repo = TripRepository(session)
            trip = await repo.get_by_id_with_access_check(trip_id, user_id)
            
            if not trip:
                return {}
            
            step_repo = StepRepository(session)
            steps = await step_repo.list_by_trip(trip.id, user_id=user_id)
            
            # Build map data
            map_data = {
                "trip": {
                    "name": trip.name,
                    "latitude": trip.latitude,
                    "longitude": trip.longitude
                },
                "steps": [],
                "colors": await repo.get_category_colors()
            }
            
            for step in steps:
                step_data = {
                    "id": step.id,
                    "name": step.name,
                    "category": step.category,
                    "type": step.type,
                    "color": step.color or map_data["colors"].get(step.category, "#666666"),
                    "is_transport": step.category == "transport"
                }
                
                # For transport, we have start and end points
                if step.category == "transport":
                    step_data["points"] = [
                        {
                            "lat": step.latitude_start,
                            "lng": step.longitude_start,
                            "label": step.location_start
                        },
                        {
                            "lat": step.latitude_end,
                            "lng": step.longitude_end,
                            "label": step.location_end
                        }
                    ]
                else:
                    # For other categories, use start point (or end if start not available)
                    lat = step.latitude_start or step.latitude_end
                    lng = step.longitude_start or step.longitude_end
                    label = step.location_start or step.location_end or step.name
                    
                    step_data["points"] = [
                        {
                            "lat": lat,
                            "lng": lng,
                            "label": label
                        }
                    ]
                
                map_data["steps"].append(step_data)
            
            return map_data
