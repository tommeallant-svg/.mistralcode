"""
Dataset models for data manipulation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from .base import BaseModel as AppBaseModel


class DatasetColumn(BaseModel):
    """Represents a column in a dataset"""
    name: str = Field(..., description="Column name")
    dtype: str = Field(..., description="Column data type")
    nullable: bool = Field(default=True, description="Whether column allows null values")
    description: Optional[str] = Field(default=None, description="Column description")
    
    class Config:
        from_attributes = True


class DatasetRow(BaseModel):
    """Represents a row in a dataset"""
    index: Optional[int] = Field(default=None, description="Row index")
    data: Dict[str, Any] = Field(default_factory=dict, description="Row data as key-value pairs")
    
    class Config:
        from_attributes = True


class Dataset(AppBaseModel):
    """Represents a dataset"""
    name: str = Field(..., description="Dataset name")
    source: str = Field(..., description="Data source (csv file path or database table)")
    description: Optional[str] = Field(default=None, description="Dataset description")
    columns: List[DatasetColumn] = Field(default_factory=list, description="List of columns")
    row_count: int = Field(default=0, description="Number of rows")
    file_path: Optional[str] = Field(default=None, description="Path to CSV file (if applicable)")
    table_name: Optional[str] = Field(default=None, description="Database table name (if applicable)")
    
    class Config:
        from_attributes = True


class DatasetCreateRequest(BaseModel):
    """Request model for creating a dataset"""
    name: str = Field(..., description="Dataset name")
    description: Optional[str] = Field(default=None, description="Dataset description")
    file: Optional[Any] = Field(default=None, description="Uploaded CSV file")
    source_path: Optional[str] = Field(default=None, description="Path to existing CSV file")


class DatasetQueryRequest(BaseModel):
    """Request model for querying a dataset"""
    dataset_name: str = Field(..., description="Dataset name")
    limit: Optional[int] = Field(default=100, description="Maximum number of rows to return")
    offset: Optional[int] = Field(default=0, description="Number of rows to skip")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Filters to apply")
    sort_by: Optional[str] = Field(default=None, description="Column to sort by")
    sort_order: Optional[str] = Field(default="asc", description="Sort order (asc or desc)")


class DatasetUpdateRequest(BaseModel):
    """Request model for updating a dataset"""
    description: Optional[str] = Field(default=None, description="New description")
    new_name: Optional[str] = Field(default=None, description="New dataset name")
