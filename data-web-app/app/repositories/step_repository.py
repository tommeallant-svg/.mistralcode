"""
Step repository for step management operations.
"""

from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, and_, desc, func
from sqlalchemy.orm import selectinload

from ..models.step import Step, StepCategory
from ..models.trip import Trip
from .base_repository import BaseRepository


class StepRepository(BaseRepository):
    """Repository for step operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, step_id: int) -> Optional[Step]:
        """Get step by ID"""
        result = await self.session.execute(
            select(Step)
            .where(Step.id == step_id)
            .options(selectinload(Step.trip))
        )
        return result.scalar_one_or_none()
    
    async def get_by_id_with_access_check(self, step_id: int, user_id: int) -> Optional[Step]:
        """Get step by ID with access check"""
        # Get step with trip
        result = await self.session.execute(
            select(Step)
            .where(Step.id == step_id)
            .options(selectinload(Step.trip))
        )
        step = result.scalar_one_or_none()
        if not step:
            return None
        
        # Check if user has access to the trip
        from ..repositories.trip_repository import TripRepository
        trip_repo = TripRepository(self.session)
        trip = await trip_repo.get_by_id_with_access_check(step.trip_id, user_id)
        if trip:
            return step
        return None
    
    async def list_by_trip(self, trip_id: int, category_filter: Optional[str] = None, 
                          user_id: Optional[int] = None) -> List[Step]:
        """List steps by trip with optional category filter and access check"""
        query = select(Step).where(Step.trip_id == trip_id)
        
        if category_filter:
            query = query.where(Step.category == category_filter)
        
        query = query.order_by(Step.order_index)
        
        result = await self.session.execute(query)
        steps = result.scalars().all()
        
        # If user_id provided, verify access to trip
        if user_id:
            from ..repositories.trip_repository import TripRepository
            trip_repo = TripRepository(self.session)
            trip = await trip_repo.get_by_id_with_access_check(trip_id, user_id)
            if not trip:
                return []
        
        return steps
    
    async def create(self, step_data: dict) -> Step:
        """Create a new step"""
        step = Step(**step_data)
        self.session.add(step)
        await self.session.commit()
        await self.session.refresh(step)
        
        # Update trip updated_at
        await self.session.execute(
            update(Trip)
            .where(Trip.id == step.trip_id)
            .values({"updated_at": func.now()})
        )
        await self.session.commit()
        
        return step
    
    async def update(self, step_id: int, update_data: dict, user_id: int) -> Optional[Step]:
        """Update a step with access check"""
        step = await self.get_by_id_with_access_check(step_id, user_id)
        if not step:
            return None
        
        result = await self.session.execute(
            update(Step)
            .where(Step.id == step_id)
            .values(**update_data)
            .returning(Step)
        )
        updated_step = result.scalar_one_or_none()
        await self.session.commit()
        
        if updated_step:
            # Update trip updated_at
            await self.session.execute(
                update(Trip)
                .where(Trip.id == updated_step.trip_id)
                .values({"updated_at": func.now()})
            )
            await self.session.commit()
            await self.session.refresh(updated_step)
        
        return updated_step
    
    async def delete(self, step_id: int, user_id: int) -> bool:
        """Delete a step with access check"""
        step = await self.get_by_id_with_access_check(step_id, user_id)
        if not step:
            return False
        
        trip_id = step.trip_id
        await self.session.delete(step)
        await self.session.commit()
        
        # Update trip updated_at
        await self.session.execute(
            update(Trip)
            .where(Trip.id == trip_id)
            .values({"updated_at": func.now()})
        )
        await self.session.commit()
        
        # Reorder remaining steps
        await self.reorder_steps(trip_id)
        
        return True
    
    async def duplicate(self, step_id: int, user_id: int) -> Optional[Step]:
        """Duplicate a step"""
        original = await self.get_by_id_with_access_check(step_id, user_id)
        if not original:
            return None
        
        new_step_data = {
            "name": f"{original.name} (copy)",
            "category": original.category,
            "type": original.type,
            "start_datetime": original.start_datetime,
            "end_datetime": original.end_datetime,
            "location_start": original.location_start,
            "location_end": original.location_end,
            "latitude_start": original.latitude_start,
            "longitude_start": original.longitude_start,
            "latitude_end": original.latitude_end,
            "longitude_end": original.longitude_end,
            "notes": original.notes,
            "order_index": original.order_index + 1,  # Place after original
            "color": original.color,
            "trip_id": original.trip_id
        }
        return await self.create(new_step_data)
    
    async def reorder_steps(self, trip_id: int) -> bool:
        """Reorder steps by order_index"""
        result = await self.session.execute(
            select(Step)
            .where(Step.trip_id == trip_id)
            .order_by(Step.order_index)
        )
        steps = result.scalars().all()
        
        for index, step in enumerate(steps):
            step.order_index = index
        
        await self.session.commit()
        return True
    
    async def set_steps_order(self, trip_id: int, step_ids: List[int], user_id: Optional[int] = None) -> bool:
        """Set custom order for steps"""
        # Verify access if user_id provided
        if user_id:
            from ..repositories.trip_repository import TripRepository
            trip_repo = TripRepository(self.session)
            trip = await trip_repo.get_by_id_with_access_check(trip_id, user_id)
            if not trip:
                return False
        
        for index, step_id in enumerate(step_ids):
            await self.session.execute(
                update(Step)
                .where(Step.id == step_id)
                .values({"order_index": index})
            )
        
        # Update trip updated_at
        await self.session.execute(
            update(Trip)
            .where(Trip.id == trip_id)
            .values({"updated_at": func.now()})
        )
        
        await self.session.commit()
        return True
    
    async def get_categories(self) -> List[str]:
        """Get all available categories"""
        return ["transport", "hébergement", "activité", "food", "sport", "hobbies"]
    
    async def get_transport_types(self) -> List[str]:
        """Get all available transport types"""
        return ["bateau", "train", "avion", "voiture", "scoot", "vélo", "marche", "bus"]
    
    async def get_colors_by_category(self) -> dict:
        """Get default colors for each category"""
        return {
            "transport": "#3B82F6",
            "hébergement": "#10B981", 
            "activité": "#F59E0B",
            "food": "#EF4444",
            "sport": "#8B5CF6",
            "hobbies": "#EC4899"
        }
