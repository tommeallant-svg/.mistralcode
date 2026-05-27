"""
PostgreSQL-based dataset repository implementation.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, MetaData, Table, Column
from sqlalchemy.exc import SQLAlchemyError

from ..config import settings
from ..models.dataset import Dataset, DatasetColumn, DatasetRow
from ..models.base import Base, DBBase
from .base import DatasetRepository

logger = logging.getLogger(__name__)


# SQLAlchemy model for storing dataset metadata in PostgreSQL
class DatasetMetadata(DBBase):
    __tablename__ = "datasets_metadata"
    
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    table_name = Column(String(255), nullable=False)
    source = Column(String(500), nullable=True)
    row_count = Column(Integer, default=0)
    column_info = Column(String, nullable=True)  # JSON string with column info


class PostgresRepository(DatasetRepository):
    """Repository for PostgreSQL-based datasets"""
    
    def __init__(self):
        self.engine = None
        self.session_maker = None
        self._connected = False
        self.database_url = settings.database.database_url
    
    async def connect(self):
        """Establish connection to PostgreSQL"""
        try:
            self.engine = create_async_engine(
                self.database_url,
                pool_size=settings.database.db_pool_size,
                max_overflow=settings.database.db_max_overflow,
                echo=False
            )
            self.session_maker = async_sessionmaker(
                self.engine,
                expire_on_commit=False,
                class_=AsyncSession
            )
            
            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            self._connected = True
            logger.info("PostgreSQL repository connected")
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def disconnect(self):
        """Close connection to PostgreSQL"""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_maker = None
            self._connected = False
            logger.info("PostgreSQL repository disconnected")
    
    async def is_connected(self) -> bool:
        """Check if connection is active"""
        return self._connected
    
    async def list_datasets(self, limit: int = 100, offset: int = 0) -> List[Dataset]:
        """List all datasets (tables) in the database"""
        if not self._connected:
            await self.connect()
        
        async with self.session_maker() as session:
            # Get metadata from our datasets_metadata table if it exists
            try:
                result = await session.execute(
                    select(DatasetMetadata).limit(limit).offset(offset)
                )
                datasets = result.scalars().all()
                
                return [
                    Dataset(
                        id=ds.id,
                        name=ds.name,
                        source=ds.source or f"postgres://{ds.table_name}",
                        description=ds.description,
                        table_name=ds.table_name,
                        row_count=ds.row_count or 0,
                        created_at=str(ds.created_at) if ds.created_at else None,
                        updated_at=str(ds.updated_at) if ds.updated_at else None
                    )
                    for ds in datasets
                ]
            except Exception as e:
                logger.error(f"Error listing datasets from metadata: {e}")
                # Fallback: list all tables
                return await self._list_all_tables(limit, offset)
    
    async def _list_all_tables(self, limit: int = 100, offset: int = 0) -> List[Dataset]:
        """List all tables in the database"""
        async with self.session_maker() as session:
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name 
                LIMIT :limit OFFSET :offset
            """), {"limit": limit, "offset": offset})
            
            tables = result.fetchall()
            
            datasets = []
            for table in tables:
                table_name = table[0]
                datasets.append(Dataset(
                    name=table_name,
                    source=f"postgres://{table_name}",
                    table_name=table_name,
                    row_count=0  # Will be populated on demand
                ))
            
            return datasets
    
    async def get_dataset(self, name: str) -> Optional[Dataset]:
        """Get a specific dataset by name"""
        if not self._connected:
            await self.connect()
        
        async with self.session_maker() as session:
            # Try to get from metadata table
            result = await session.execute(
                select(DatasetMetadata).where(DatasetMetadata.name == name)
            )
            metadata = result.scalar_one_or_none()
            
            if metadata:
                return Dataset(
                    id=metadata.id,
                    name=metadata.name,
                    source=metadata.source or f"postgres://{metadata.table_name}",
                    description=metadata.description,
                    table_name=metadata.table_name,
                    row_count=metadata.row_count or 0,
                    created_at=str(metadata.created_at) if metadata.created_at else None,
                    updated_at=str(metadata.updated_at) if metadata.updated_at else None
                )
            
            # Check if table exists
            result = await session.execute(text("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = :name
                )
            """), {"name": name})
            
            if result.scalar():
                return Dataset(
                    name=name,
                    source=f"postgres://{name}",
                    table_name=name,
                    row_count=0
                )
            
            return None
    
    async def create_dataset(self, name: str, description: Optional[str] = None,
                           source: Optional[str] = None) -> Dataset:
        """Create a new dataset (table) in PostgreSQL"""
        if not self._connected:
            await self.connect()
        
        async with self.session_maker() as session:
            # Create metadata entry
            dataset_metadata = DatasetMetadata(
                name=name,
                description=description,
                table_name=name,
                source=source,
                row_count=0
            )
            session.add(dataset_metadata)
            await session.commit()
            
            return Dataset(
                id=dataset_metadata.id,
                name=name,
                source=source or f"postgres://{name}",
                description=description,
                table_name=name,
                row_count=0,
                created_at=str(dataset_metadata.created_at)
            )
    
    async def delete_dataset(self, name: str) -> bool:
        """Delete a dataset (table) from PostgreSQL"""
        if not self._connected:
            await self.connect()
        
        async with self.session_maker() as session:
            try:
                # Delete from metadata
                result = await session.execute(
                    select(DatasetMetadata).where(DatasetMetadata.name == name)
                )
                metadata = result.scalar_one_or_none()
                if metadata:
                    await session.delete(metadata)
                
                # Drop the table
                await session.execute(text(f'DROP TABLE IF EXISTS "{name}" CASCADE'))
                await session.commit()
                logger.info(f"Deleted dataset: {name}")
                return True
            except Exception as e:
                logger.error(f"Error deleting dataset {name}: {e}")
                await session.rollback()
                return False
    
    async def query_dataset(self, name: str, limit: int = 100, offset: int = 0,
                           filters: Optional[Dict[str, Any]] = None,
                           sort_by: Optional[str] = None,
                           sort_order: str = "asc") -> Dict[str, Any]:
        """Query data from a PostgreSQL table"""
        if not self._connected:
            await self.connect()
        
        async with self.session_maker() as session:
            # Get table metadata
            table = Table(name, MetaData(), autoload_with=self.engine.sync_engine)
            
            # Build query
            query = select(table).limit(limit).offset(offset)
            
            # Apply sorting
            if sort_by:
                column = table.c.get(sort_by)
                if column:
                    if sort_order.lower() == "desc":
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column.asc())
            
            # Execute query
            result = await session.execute(query)
            rows = result.fetchall()
            
            # Get total count
            count_result = await session.execute(select([text("count(*)")]).select_from(table))
            total_rows = count_result.scalar()
            
            # Get column info
            columns = [
                DatasetColumn(
                    name=str(col.name),
                    dtype=str(col.type),
                    nullable=col.nullable
                )
                for col in table.columns
            ]
            
            # Convert rows to dict format
            rows_data = []
            for idx, row in enumerate(rows):
                rows_data.append(DatasetRow(
                    index=offset + idx,
                    data=dict(row._asdict())
                ))
            
            return {
                "dataset_name": name,
                "columns": columns,
                "rows": rows_data,
                "total_rows": total_rows,
                "returned_rows": len(rows_data)
            }
    
    async def get_dataset_columns(self, name: str) -> List[DatasetColumn]:
        """Get column information for a dataset"""
        if not self._connected:
            await self.connect()
        
        async with self.session_maker() as session:
            table = Table(name, MetaData(), autoload_with=self.engine.sync_engine)
            
            return [
                DatasetColumn(
                    name=str(col.name),
                    dtype=str(col.type),
                    nullable=col.nullable
                )
                for col in table.columns
            ]
    
    async def get_dataset_stats(self, name: str) -> Dict[str, Any]:
        """Get statistics for a dataset"""
        if not self._connected:
            await self.connect()
        
        async with self.session_maker() as session:
            table = Table(name, MetaData(), autoload_with=self.engine.sync_engine)
            
            # Get row count
            result = await session.execute(select([text("count(*)")]).select_from(table))
            row_count = result.scalar()
            
            stats = {
                "row_count": row_count,
                "column_count": len(table.columns),
                "column_stats": {}
            }
            
            # Get stats for each numeric column
            for col in table.columns:
                col_name = col.name
                
                # Get basic stats
                result = await session.execute(text(f"""
                    SELECT 
                        COUNT({col_name}) as count,
                        COUNT(*) FILTER (WHERE {col_name} IS NULL) as null_count,
                        COUNT(DISTINCT {col_name}) as unique_count,
                        MIN({col_name}) as min_val,
                        MAX({col_name}) as max_val,
                        AVG({col_name}) as avg_val
                    FROM {name}
                """))
                
                row = result.fetchone()
                
                stats["column_stats"][col_name] = {
                    "dtype": str(col.type),
                    "nullable": col.nullable,
                    "null_count": row.null_count if row else 0,
                    "unique_count": row.unique_count if row else 0,
                    "min": row.min_val if row else None,
                    "max": row.max_val if row else None,
                    "mean": row.avg_val if row else None,
                }
            
            return stats
