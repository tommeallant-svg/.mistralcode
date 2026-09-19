"""
SharedTrip repository for trip sharing operations.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, and_, or_
from sqlalchemy.orm import selectinload

from ..models.shared_trip import SharedTrip
from ..models.user import User
from ..models.trip import Trip
from .base_repository import BaseRepository


class SharedTripRepository(BaseRepository):
    """Repository for shared trip operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, shared_trip_id: int) -> Optional[SharedTrip]:
        """Get shared trip by ID"""
        result = await self.session.execute(
            select(SharedTrip)
            .where(SharedTrip.id == shared_trip_id)
            .options(
                selectinload(SharedTrip.user),
                selectinload(SharedTrip.shared_with_user),
                selectinload(SharedTrip.trip)
            )
        )
        return result.scalar_one_or_none()
    
    async def list_by_user(self, user_id: int, limit: int = 100, offset: int = 0) -> List[SharedTrip]:
        """List shared trips where user is the owner"""
        result = await self.session.execute(
            select(SharedTrip)
            .where(SharedTrip.user_id == user_id)
            .options(
                selectinload(SharedTrip.user),
                selectinload(SharedTrip.shared_with_user),
                selectinload(SharedTrip.trip)
            )
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def list_shared_with_user(self, user_id: int, limit: int = 100, offset: int = 0) -> List[SharedTrip]:
        """List shared trips where user is the one with whom it's shared"""
        result = await self.session.execute(
            select(SharedTrip)
            .where(SharedTrip.shared_with_user_id == user_id)
            .options(
                selectinload(SharedTrip.user),
                selectinload(SharedTrip.shared_with_user),
                selectinload(SharedTrip.trip)
            )
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def create(self, shared_trip_data: dict) -> SharedTrip:
        """Create a new shared trip"""
        shared_trip = SharedTrip(**shared_trip_data)
        self.session.add(shared_trip)
        await self.session.commit()
        await self.session.refresh(shared_trip)
        return shared_trip
    
    async def update(self, shared_trip_id: int, update_data: dict, user_id: int) -> Optional[SharedTrip]:
        """Update a shared trip with access check"""
        # Verify user is the owner of the shared trip
        result = await self.session.execute(
            select(SharedTrip).where(
                and_(
                    SharedTrip.id == shared_trip_id,
                    SharedTrip.user_id == user_id
                )
            )
        )
        shared_trip = result.scalar_one_or_none()
        if not shared_trip:
            return None
        
        result = await self.session.execute(
            update(SharedTrip)
            .where(SharedTrip.id == shared_trip_id)
            .values(**update_data)
            .returning(SharedTrip)
        )
        updated = result.scalar_one_or_none()
        await self.session.commit()
        if updated:
            await self.session.refresh(updated)
        return updated
    
    async def delete(self, shared_trip_id: int, user_id: int) -> bool:
        """Delete a shared trip with access check"""
        # Verify user is the owner
        result = await self.session.execute(
            select(SharedTrip).where(
                and_(
                    SharedTrip.id == shared_trip_id,
                    SharedTrip.user_id == user_id
                )
            )
        )
        shared_trip = result.scalar_one_or_none()
        if not shared_trip:
            return False
        
        await self.session.delete(shared_trip)
        await self.session.commit()
        return True
    
    async def is_shared_with_user(self, trip_id: int, user_id: int) -> bool:
        """Check if a trip is shared with a user"""
        result = await self.session.execute(
            select(SharedTrip).where(
                and_(
                    SharedTrip.trip_id == trip_id,
                    SharedTrip.shared_with_user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def get_users_with_access(self, trip_id: int) -> List[User]:
        """Get all users with access to a trip (owner + shared)"""
        # Get owner
        result = await self.session.execute(
            select(Trip).where(Trip.id == trip_id)
        )
        trip = result.scalar_one_or_none()
        
        if not trip:
            return []
        
        users = []
        
        # Add owner
        result = await self.session.execute(
            select(User).where(User.id == trip.owner_id)
        )
        owner = result.scalar_one_or_none()
        if owner:
            users.append(owner)
        
        # Add shared users
        result = await self.session.execute(
            select(SharedTrip).where(SharedTrip.trip_id == trip_id)
        )
        shared_trips = result.scalars().all()
        
        for st in shared_trips:
            result = await self.session.execute(
                select(User).where(User.id == st.shared_with_user_id)
            )
            user = result.scalar_one_or_none()
            if user and user not in users:
                users.append(user)
        
        return users
