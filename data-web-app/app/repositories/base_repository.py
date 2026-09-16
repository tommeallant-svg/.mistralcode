"""
Base repository class for all repositories.
"""

from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository(ABC):
    """Base repository class"""
    
    @abstractmethod
    def __init__(self, session: AsyncSession):
        """Initialize with async session"""
        self.session = session
