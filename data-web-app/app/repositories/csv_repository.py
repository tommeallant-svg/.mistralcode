"""
CSV-based dataset repository implementation.
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path
import pandas as pd
import logging

from ..config import settings
from ..models.dataset import Dataset, DatasetColumn, DatasetRow
from .base import DatasetRepository

logger = logging.getLogger(__name__)


class CSVRepository(DatasetRepository):
    """Repository for CSV file-based datasets"""
    
    def __init__(self):
        self.csv_directory = Path(settings.csv.csv_directory)
        self.upload_directory = Path(settings.csv.upload_directory)
        self._connected = False
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        self.csv_directory.mkdir(parents=True, exist_ok=True)
        self.upload_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"CSV directories ensured: {self.csv_directory}, {self.upload_directory}")
    
    async def connect(self):
        """Establish connection (for CSV, just ensure directories exist)"""
        self._ensure_directories()
        self._connected = True
        logger.info("CSV repository connected")
    
    async def disconnect(self):
        """Close connection"""
        self._connected = False
        logger.info("CSV repository disconnected")
    
    async def is_connected(self) -> bool:
        """Check if connection is active"""
        return self._connected
    
    async def list_datasets(self, limit: int = 100, offset: int = 0) -> List[Dataset]:
        """List all CSV datasets in the directory"""
        if not self._connected:
            await self.connect()
        
        datasets = []
        csv_files = list(self.csv_directory.glob("*.csv"))
        
        for csv_file in csv_files[offset:offset + limit]:
            try:
                dataset = await self._load_csv_metadata(csv_file)
                datasets.append(dataset)
            except Exception as e:
                logger.error(f"Error loading dataset from {csv_file}: {e}")
                continue
        
        return datasets
    
    async def get_dataset(self, name: str) -> Optional[Dataset]:
        """Get a specific dataset by name"""
        if not self._connected:
            await self.connect()
        
        csv_path = self.csv_directory / f"{name}.csv"
        if not csv_path.exists():
            return None
        
        return await self._load_csv_metadata(csv_path)
    
    async def create_dataset(self, name: str, description: Optional[str] = None,
                           source: Optional[str] = None) -> Dataset:
        """Create a new dataset from a CSV file"""
        if not self._connected:
            await self.connect()
        
        # If source is provided, copy the file
        if source:
            source_path = Path(source)
            if source_path.exists():
                target_path = self.csv_directory / f"{name}.csv"
                await asyncio.to_thread(source_path.rename, target_path)
            else:
                raise FileNotFoundError(f"Source file not found: {source}")
        else:
            # Create empty CSV file
            target_path = self.csv_directory / f"{name}.csv"
            await asyncio.to_thread(lambda: Path(target_path).touch())
        
        # Load metadata
        target_path = self.csv_directory / f"{name}.csv"
        dataset = await self._load_csv_metadata(target_path)
        dataset.description = description or dataset.description
        
        return dataset
    
    async def delete_dataset(self, name: str) -> bool:
        """Delete a dataset by name"""
        csv_path = self.csv_directory / f"{name}.csv"
        if csv_path.exists():
            await asyncio.to_thread(csv_path.unlink)
            logger.info(f"Deleted dataset: {name}")
            return True
        return False
    
    async def query_dataset(self, name: str, limit: int = 100, offset: int = 0,
                           filters: Optional[Dict[str, Any]] = None,
                           sort_by: Optional[str] = None,
                           sort_order: str = "asc") -> Dict[str, Any]:
        """Query data from a CSV dataset"""
        if not self._connected:
            await self.connect()
        
        csv_path = self.csv_directory / f"{name}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset {name} not found")
        
        # Read CSV with pandas
        df = await asyncio.to_thread(pd.read_csv, str(csv_path))
        
        # Apply filters
        if filters:
            for column, value in filters.items():
                if column in df.columns:
                    df = df[df[column] == value]
        
        # Apply sorting
        if sort_by and sort_by in df.columns:
            ascending = sort_order.lower() == "asc"
            df = df.sort_values(by=sort_by, ascending=ascending)
        
        # Apply limit and offset
        total_rows = len(df)
        df = df.iloc[offset:offset + limit]
        
        # Convert to dataset response format
        columns = [
            DatasetColumn(
                name=str(col),
                dtype=str(dtype),
                nullable=df[col].isna().any()
            )
            for col, dtype in zip(df.columns, df.dtypes)
        ]
        
        rows = [
            DatasetRow(
                index=int(idx),
                data=row.to_dict()
            )
            for idx, row in df.iterrows()
        ]
        
        return {
            "dataset_name": name,
            "columns": columns,
            "rows": rows,
            "total_rows": total_rows,
            "returned_rows": len(rows)
        }
    
    async def get_dataset_columns(self, name: str) -> List[DatasetColumn]:
        """Get column information for a dataset"""
        if not self._connected:
            await self.connect()
        
        csv_path = self.csv_directory / f"{name}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset {name} not found")
        
        df = await asyncio.to_thread(pd.read_csv, str(csv_path), nrows=0)
        
        return [
            DatasetColumn(
                name=str(col),
                dtype=str(dtype),
                nullable=True  # Can't determine nullability without reading data
            )
            for col, dtype in zip(df.columns, df.dtypes)
        ]
    
    async def get_dataset_stats(self, name: str) -> Dict[str, Any]:
        """Get statistics for a dataset"""
        if not self._connected:
            await self.connect()
        
        csv_path = self.csv_directory / f"{name}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset {name} not found")
        
        df = await asyncio.to_thread(pd.read_csv, str(csv_path))
        
        stats = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "memory_usage": str(df.memory_usage(deep=True).sum()) + " bytes",
            "column_stats": {}
        }
        
        for col in df.columns:
            col_data = df[col]
            stats["column_stats"][col] = {
                "dtype": str(col_data.dtype),
                "null_count": int(col_data.isna().sum()),
                "unique_count": int(col_data.nunique()),
                "mean": float(col_data.mean()) if pd.api.types.is_numeric_dtype(col_data) else None,
                "min": float(col_data.min()) if pd.api.types.is_numeric_dtype(col_data) else None,
                "max": float(col_data.max()) if pd.api.types.is_numeric_dtype(col_data) else None,
            }
        
        return stats
    
    async def _load_csv_metadata(self, csv_path: Path) -> Dataset:
        """Load metadata from a CSV file"""
        # Read just the header to get column info
        df = await asyncio.to_thread(pd.read_csv, str(csv_path), nrows=0)
        
        columns = [
            DatasetColumn(
                name=str(col),
                dtype=str(dtype),
                nullable=True
            )
            for col, dtype in zip(df.columns, df.dtypes)
        ]
        
        # Count rows (efficiently)
        row_count = await asyncio.to_thread(
            lambda: sum(1 for _ in open(str(csv_path), 'r')) - 1
        )
        
        return Dataset(
            name=csv_path.stem,
            source=str(csv_path),
            file_path=str(csv_path),
            columns=columns,
            row_count=max(0, row_count)  # Ensure non-negative
        )
