"""
Dataset service for business logic operations.
"""

from typing import Optional, List, Dict, Any, Union
import logging

from ..config import settings
from ..repositories.csv_repository import CSVRepository
from ..repositories.postgres_repository import PostgresRepository
from ..models.dataset import Dataset, DatasetCreateRequest, DatasetQueryRequest
from ..schemas.dataset import DatasetResponse, DatasetListResponse, DatasetQueryResponse

logger = logging.getLogger(__name__)


class DatasetService:
    """Service for dataset operations"""
    
    def __init__(self):
        self.data_source = settings.app.data_source
        self.repository = self._get_repository()
    
    def _get_repository(self):
        """Get the appropriate repository based on data source"""
        if self.data_source == "postgres":
            logger.info("Using PostgreSQL repository")
            return PostgresRepository()
        else:
            logger.info("Using CSV repository (default)")
            return CSVRepository()
    
    async def initialize(self):
        """Initialize the service"""
        await self.repository.connect()
    
    async def shutdown(self):
        """Shutdown the service"""
        await self.repository.disconnect()
    
    async def list_datasets(self, limit: int = 100, offset: int = 0) -> DatasetListResponse:
        """List all datasets"""
        datasets = await self.repository.list_datasets(limit=limit, offset=offset)
        
        return DatasetListResponse(
            datasets=[
                DatasetResponse(
                    id=ds.id,
                    name=ds.name,
                    source=ds.source,
                    description=ds.description,
                    columns=ds.columns,
                    row_count=ds.row_count,
                    file_path=ds.file_path,
                    table_name=ds.table_name,
                    created_at=ds.created_at,
                    updated_at=ds.updated_at
                )
                for ds in datasets
            ],
            total=len(datasets),
            limit=limit,
            offset=offset
        )
    
    async def get_dataset(self, name: str) -> Optional[DatasetResponse]:
        """Get a specific dataset by name"""
        dataset = await self.repository.get_dataset(name)
        
        if dataset:
            return DatasetResponse(
                id=dataset.id,
                name=dataset.name,
                source=dataset.source,
                description=dataset.description,
                columns=dataset.columns,
                row_count=dataset.row_count,
                file_path=dataset.file_path,
                table_name=dataset.table_name,
                created_at=dataset.created_at,
                updated_at=dataset.updated_at
            )
        return None
    
    async def create_dataset(self, request: DatasetCreateRequest) -> DatasetResponse:
        """Create a new dataset"""
        # Handle file upload
        source_path = None
        if hasattr(request, 'file') and request.file:
            # Save uploaded file to temporary location
            import tempfile
            import os
            from pathlib import Path
            
            temp_dir = Path(settings.csv.upload_directory)
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = temp_dir / request.file.filename
            with open(file_path, "wb") as f:
                f.write(await request.file.read())
            
            source_path = str(file_path)
        
        dataset = await self.repository.create_dataset(
            name=request.name,
            description=request.description,
            source=source_path or request.source_path
        )
        
        return DatasetResponse(
            name=dataset.name,
            source=dataset.source,
            description=dataset.description,
            columns=dataset.columns,
            row_count=dataset.row_count,
            file_path=dataset.file_path,
            table_name=dataset.table_name
        )
    
    async def delete_dataset(self, name: str) -> bool:
        """Delete a dataset by name"""
        return await self.repository.delete_dataset(name)
    
    async def query_dataset(self, request: DatasetQueryRequest) -> DatasetQueryResponse:
        """Query data from a dataset"""
        result = await self.repository.query_dataset(
            name=request.dataset_name,
            limit=request.limit or 100,
            offset=request.offset or 0,
            filters=request.filters,
            sort_by=request.sort_by,
            sort_order=request.sort_order or "asc"
        )
        
        return DatasetQueryResponse(
            dataset_name=result["dataset_name"],
            columns=result["columns"],
            rows=result["rows"],
            total_rows=result["total_rows"],
            returned_rows=result["returned_rows"],
            limit=result["returned_rows"],
            offset=request.offset or 0
        )
    
    async def get_dataset_columns(self, name: str) -> List[Dict[str, Any]]:
        """Get column information for a dataset"""
        columns = await self.repository.get_dataset_columns(name)
        
        return [
            {
                "name": col.name,
                "dtype": col.dtype,
                "nullable": col.nullable,
                "description": col.description
            }
            for col in columns
        ]
    
    async def get_dataset_stats(self, name: str) -> Dict[str, Any]:
        """Get statistics for a dataset"""
        return await self.repository.get_dataset_stats(name)
    
    async def import_csv_to_postgres(self, dataset_name: str, table_name: Optional[str] = None) -> bool:
        """Import a CSV dataset to PostgreSQL"""
        # This is a special method for migrating from CSV to PostgreSQL
        # For now, this is a placeholder - would need implementation
        logger.info(f"Importing {dataset_name} to PostgreSQL")
        # Implementation would:
        # 1. Get CSV data
        # 2. Create PostgreSQL table
        # 3. Insert data
        # 4. Update metadata
        return True
