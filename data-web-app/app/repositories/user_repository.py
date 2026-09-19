"""
User repository for user management operations.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.exc import IntegrityError

from ..models.user import User
from ..models.base import DBBase
from .base_repository import BaseRepository


class UserRepository(BaseRepository):
    """Repository for user operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List all users"""
        result = await self.session.execute(
            select(User).limit(limit).offset(offset)
        )
        return result.scalars().all()
    
    async def create(self, user_data: dict) -> User:
        """Create a new user"""
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def update(self, user_id: int, update_data: dict) -> Optional[User]:
        """Update a user"""
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
            .returning(User)
        )
        updated_user = result.scalar_one_or_none()
        await self.session.commit()
        return updated_user
    
    async def delete(self, user_id: int) -> bool:
        """Delete a user"""
        result = await self.session.execute(
            delete(User).where(User.id == user_id)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_hardcoded_user(self) -> Optional[User]:
        """Get the hardcoded user 'Paloma' with password 'laBest'"""
        # Try to find existing Paloma user
        user = await self.get_by_username("Paloma")
        if user:
            return user
        
        # Create Paloma user if doesn't exist
        # Password hash for 'laBest' (pre-hashed for demo purposes)
        # In production, use proper password hashing
        import hashlib
        password_hash = hashlib.sha256("laBest".encode()).hexdigest()
        
        user_data = {
            "username": "Paloma",
            "password_hash": password_hash,
            "full_name": "Paloma User",
            "email": "paloma@example.com",
            "is_active": True,
            "is_superuser": True
        }
        return await self.create(user_data)
