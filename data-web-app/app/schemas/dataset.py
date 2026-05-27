"""
Pydantic schemas for dataset responses.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from ..models.dataset import Dataset, DatasetColumn, DatasetRow


class ErrorResponse(BaseModel):
    """Standard error response schema"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error message")
    status_code: int = Field(default=400, description="HTTP status code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Dataset not found",
                "detail": "The requested dataset does not exist",
                "status_code": 404
            }
        }


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="Application version")
    data_source: str = Field(..., description="Current data source")
    timestamp: str = Field(..., description="Timestamp of the check")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "data_source": "csv",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class DatasetResponse(BaseModel):
    """Response schema for a single dataset"""
    id: Optional[int] = Field(default=None, description="Dataset ID")
    name: str = Field(..., description="Dataset name")
    source: str = Field(..., description="Data source")
    description: Optional[str] = Field(default=None, description="Dataset description")
    columns: List[DatasetColumn] = Field(default_factory=list, description="List of columns")
    row_count: int = Field(default=0, description="Number of rows")
    file_path: Optional[str] = Field(default=None, description="Path to CSV file")
    table_name: Optional[str] = Field(default=None, description="Database table name")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "sample_dataset",
                "source": "data/csv/sample.csv",
                "description": "Sample CSV dataset",
                "columns": [
                    {"name": "id", "dtype": "int64", "nullable": False},
                    {"name": "name", "dtype": "object", "nullable": True}
                ],
                "row_count": 1000,
                "file_path": "data/csv/sample.csv",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }


class DatasetCreateResponse(BaseModel):
    """Response schema for dataset creation"""
    success: bool = Field(..., description="Whether creation was successful")
    dataset: DatasetResponse = Field(..., description="Created dataset")
    message: Optional[str] = Field(default=None, description="Success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "dataset": {
                    "name": "new_dataset",
                    "source": "data/csv/new_dataset.csv",
                    "row_count": 500
                },
                "message": "Dataset created successfully"
            }
        }


class DatasetListResponse(BaseModel):
    """Response schema for listing datasets"""
    datasets: List[DatasetResponse] = Field(default_factory=list, description="List of datasets")
    total: int = Field(default=0, description="Total number of datasets")
    limit: int = Field(default=100, description="Maximum number of datasets returned")
    offset: int = Field(default=0, description="Number of datasets skipped")
    
    class Config:
        json_schema_extra = {
            "example": {
                "datasets": [
                    {
                        "name": "dataset1",
                        "source": "data/csv/dataset1.csv",
                        "row_count": 1000
                    }
                ],
                "total": 1,
                "limit": 100,
                "offset": 0
            }
        }


class DatasetQueryResponse(BaseModel):
    """Response schema for dataset query results"""
    dataset_name: str = Field(..., description="Dataset name")
    columns: List[DatasetColumn] = Field(default_factory=list, description="List of columns")
    rows: List[DatasetRow] = Field(default_factory=list, description="List of rows")
    total_rows: int = Field(default=0, description="Total number of rows")
    returned_rows: int = Field(default=0, description="Number of rows returned")
    limit: int = Field(default=100, description="Query limit")
    offset: int = Field(default=0, description="Query offset")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dataset_name": "sample_dataset",
                "columns": [
                    {"name": "id", "dtype": "int64"},
                    {"name": "name", "dtype": "object"}
                ],
                "rows": [
                    {"index": 0, "data": {"id": 1, "name": "Alice"}},
                    {"index": 1, "data": {"id": 2, "name": "Bob"}}
                ],
                "total_rows": 1000,
                "returned_rows": 2,
                "limit": 100,
                "offset": 0
            }
        }
