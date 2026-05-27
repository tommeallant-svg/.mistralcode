"""
Base repository interfaces.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from ..models.dataset import Dataset, DatasetColumn, DatasetRow


class BaseRepository(ABC):
    """Base repository interface"""
    
    @abstractmethod
    async def connect(self):
        """Establish connection to the data source"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Close connection to the data source"""
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if connection is active"""
        pass


class DatasetRepository(ABC):
    """Abstract base class for dataset operations"""
    
    @abstractmethod
    async def list_datasets(self, limit: int = 100, offset: int = 0) -> List[Dataset]:
        """List all available datasets"""
        pass
    
    @abstractmethod
    async def get_dataset(self, name: str) -> Optional[Dataset]:
        """Get a specific dataset by name"""
        pass
    
    @abstractmethod
    async def create_dataset(self, name: str, description: Optional[str] = None, 
                           source: Optional[str] = None) -> Dataset:
        """Create a new dataset"""
        pass
    
    @abstractmethod
    async def delete_dataset(self, name: str) -> bool:
        """Delete a dataset by name"""
        pass
    
    @abstractmethod
    async def query_dataset(self, name: str, limit: int = 100, offset: int = 0,
                           filters: Optional[Dict[str, Any]] = None,
                           sort_by: Optional[str] = None,
                           sort_order: str = "asc") -> Dict[str, Any]:
        """Query data from a dataset"""
        pass
    
    @abstractmethod
    async def get_dataset_columns(self, name: str) -> List[DatasetColumn]:
        """Get column information for a dataset"""
        pass
    
    @abstractmethod
    async def get_dataset_stats(self, name: str) -> Dict[str, Any]:
        """Get statistics for a dataset"""
        pass
