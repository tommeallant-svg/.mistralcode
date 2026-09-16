"""
Trip repository for trip management operations.
"""

from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, or_, and_, func, desc
from sqlalchemy.orm import joinedload, selectinload

from ..models.trip import Trip, TripStatus
from ..models.user import User
from ..models.shared_trip import SharedTrip
from .base_repository import BaseRepository


class TripRepository(BaseRepository):
    """Repository for trip operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, trip_id: int) -> Optional[Trip]:
        """Get trip by ID"""
        result = await self.session.execute(
            select(Trip)
            .where(Trip.id == trip_id)
            .options(selectinload(Trip.owner), selectinload(Trip.steps))
        )
        return result.scalar_one_or_none()
    
    async def get_by_id_with_access_check(self, trip_id: int, user_id: int) -> Optional[Trip]:
        """Get trip by ID with access check (owner or shared)"""
        # Check if user is owner
        result = await self.session.execute(
            select(Trip)
            .where(
                and_(
                    Trip.id == trip_id,
                    Trip.owner_id == user_id
                )
            )
            .options(selectinload(Trip.owner), selectinload(Trip.steps))
        )
        trip = result.scalar_one_or_none()
        if trip:
            return trip
        
        # Check if trip is shared with user
        result = await self.session.execute(
            select(SharedTrip)
            .where(
                and_(
                    SharedTrip.trip_id == trip_id,
                    SharedTrip.shared_with_user_id == user_id
                )
            )
        )
        shared = result.scalar_one_or_none()
        if shared:
            result = await self.session.execute(
                select(Trip)
                .where(Trip.id == trip_id)
                .options(selectinload(Trip.owner), selectinload(Trip.steps))
            )
            return result.scalar_one_or_none()
        
        return None
    
    async def list_by_owner(self, owner_id: int, limit: int = 100, offset: int = 0, 
                           status_filter: Optional[str] = None) -> Tuple[List[Trip], int]:
        """List trips by owner with optional status filter"""
        query = select(Trip).where(Trip.owner_id == owner_id)
        
        if status_filter:
            query = query.where(Trip.status == status_filter)
        
        # Count total
        count_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()
        
        # Get trips
        query = query.limit(limit).offset(offset).order_by(desc(Trip.created_at))
        result = await self.session.execute(
            query.options(selectinload(Trip.owner), selectinload(Trip.steps))
        )
        trips = result.scalars().all()
        
        return trips, total
    
    async def list_shared_with_user(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Trip]:
        """List trips shared with a user"""
        result = await self.session.execute(
            select(SharedTrip)
            .where(SharedTrip.shared_with_user_id == user_id)
            .options(joinedload(SharedTrip.trip).joinedload(Trip.owner))
            .limit(limit)
            .offset(offset)
            .order_by(desc(SharedTrip.created_at))
        )
        shared_trips = result.scalars().all()
        return [st.trip for st in shared_trips]
    
    async def list_all_for_user(self, user_id: int, limit: int = 100, offset: int = 0,
                               status_filter: Optional[str] = None) -> Tuple[List[Trip], int]:
        """List all trips accessible by a user (owned + shared)"""
        # Get owned trips
        owned_query = select(Trip).where(Trip.owner_id == user_id)
        if status_filter:
            owned_query = owned_query.where(Trip.status == status_filter)
        
        # Get shared trip IDs
        shared_result = await self.session.execute(
            select(SharedTrip.trip_id)
            .where(SharedTrip.shared_with_user_id == user_id)
        )
        shared_trip_ids = [row.trip_id for row in shared_result.all()]
        
        # Combine queries
        from sqlalchemy import or_
        combined_query = select(Trip).where(
            or_(
                Trip.owner_id == user_id,
                Trip.id.in_(shared_trip_ids)
            )
        )
        
        if status_filter:
            combined_query = combined_query.where(Trip.status == status_filter)
        
        # Count
        count_result = await self.session.execute(
            select(func.count()).select_from(combined_query.subquery())
        )
        total = count_result.scalar()
        
        # Get trips
        combined_query = combined_query.limit(limit).offset(offset).order_by(desc(Trip.created_at))
        result = await self.session.execute(
            combined_query.options(selectinload(Trip.owner), selectinload(Trip.steps))
        )
        trips = result.scalars().all()
        
        return trips, total
    
    async def create(self, trip_data: dict) -> Trip:
        """Create a new trip"""
        trip = Trip(**trip_data)
        self.session.add(trip)
        await self.session.commit()
        await self.session.refresh(trip)
        return trip
    
    async def update(self, trip_id: int, update_data: dict, user_id: int) -> Optional[Trip]:
        """Update a trip with access check"""
        # Verify access
        trip = await self.get_by_id_with_access_check(trip_id, user_id)
        if not trip:
            return None
        
        result = await self.session.execute(
            update(Trip)
            .where(Trip.id == trip_id)
            .values(**update_data)
            .returning(Trip)
        )
        updated_trip = result.scalar_one_or_none()
        await self.session.commit()
        if updated_trip:
            await self.session.refresh(updated_trip)
        return updated_trip
    
    async def delete(self, trip_id: int, user_id: int) -> bool:
        """Delete a trip with access check"""
        # Verify user is owner
        result = await self.session.execute(
            select(Trip).where(
                and_(Trip.id == trip_id, Trip.owner_id == user_id)
            )
        )
        trip = result.scalar_one_or_none()
        if not trip:
            return False
        
        await self.session.delete(trip)
        await self.session.commit()
        return True
    
    async def duplicate(self, trip_id: int, user_id: int, new_name: str) -> Optional[Trip]:
        """Duplicate a trip"""
        original = await self.get_by_id_with_access_check(trip_id, user_id)
        if not original:
            return None
        
        # Create new trip with same data but new ID
        new_trip_data = {
            "name": new_name,
            "description": original.description,
            "start_date": original.start_date,
            "end_date": original.end_date,
            "status": "brouillon",
            "latitude": original.latitude,
            "longitude": original.longitude,
            "owner_id": user_id
        }
        new_trip = Trip(**new_trip_data)
        self.session.add(new_trip)
        await self.session.commit()
        await self.session.refresh(new_trip)
        
        # Duplicate steps
        for step in original.steps:
            new_step = step.__class__(
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
                trip_id=new_trip.id
            )
            self.session.add(new_step)
        
        await self.session.commit()
        return new_trip
    
    async def get_category_colors(self) -> dict:
        """Get color mapping for categories"""
        return {
            "transport": "#3B82F6",  # Blue
            "hébergement": "#10B981",  # Green
            "activité": "#F59E0B",  # Orange
            "food": "#EF4444",  # Red
            "sport": "#8B5CF6",  # Purple
            "hobbies": "#EC4899"  # Pink
        }
