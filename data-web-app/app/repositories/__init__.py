"""
Data repository interfaces and implementations.
"""

from .base import BaseRepository, DatasetRepository
from .csv_repository import CSVRepository
from .postgres_repository import PostgresRepository

__all__ = [
    "BaseRepository",
    "DatasetRepository",
    "CSVRepository", 
    "PostgresRepository",
]
