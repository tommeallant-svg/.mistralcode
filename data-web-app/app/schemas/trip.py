"""
Pydantic schemas for Trip model.
"""

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field
from datetime import datetime
from .user import UserResponse

if TYPE_CHECKING:
    from .step import StepResponse


class TripBase(BaseModel):
    """Base trip schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Trip name")
    description: Optional[str] = Field(default=None, description="Trip description")
    start_date: datetime = Field(..., description="Departure date")
    end_date: datetime = Field(..., description="Return date")
    status: str = Field(default="brouillon", description="Trip status (brouillon/validé)")
    latitude: Optional[float] = Field(default=None, ge=-90, le=90, description="GPS latitude")
    longitude: Optional[float] = Field(default=None, ge=-180, le=180, description="GPS longitude")


class TripCreate(TripBase):
    """Schema for creating a trip"""
    pass


class TripUpdate(BaseModel):
    """Schema for updating a trip"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    status: Optional[str] = Field(default=None)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)


class TripResponse(TripBase):
    """Full trip response schema"""
    id: int = Field(..., description="Trip ID")
    owner_id: int = Field(..., description="Owner user ID")
    owner: Optional[UserResponse] = Field(default=None, description="Owner user")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    steps: List["StepResponse"] = Field(default_factory=list, description="List of steps")
    steps_count: int = Field(default=0, description="Number of steps")
    
    class Config:
        from_attributes = True


class TripListResponse(BaseModel):
    """Response schema for listing trips"""
    trips: List[TripResponse] = Field(default_factory=list, description="List of trips")
    total: int = Field(default=0, description="Total number of trips")
    limit: int = Field(default=100, description="Maximum number of trips returned")
    offset: int = Field(default=0, description="Number of trips skipped")


class TripSummaryResponse(BaseModel):
    """Simplified trip response for lists"""
    id: int = Field(..., description="Trip ID")
    name: str = Field(..., description="Trip name")
    status: str = Field(..., description="Trip status")
    start_date: datetime = Field(..., description="Departure date")
    end_date: datetime = Field(..., description="Return date")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    latitude: Optional[float] = Field(default=None, description="GPS latitude")
    longitude: Optional[float] = Field(default=None, description="GPS longitude")
    steps_count: int = Field(default=0, description="Number of steps")
    
    class Config:
        from_attributes = True


class TripTableRow(BaseModel):
    """Schema for trip table row (for frontend table display)"""
    id: int = Field(..., description="Trip ID")
    name: str = Field(..., description="Trip name")
    status: str = Field(..., description="Trip status")
    date_creation: datetime = Field(..., description="Creation date")
    date_modification: Optional[datetime] = Field(default=None, description="Modification date")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Voyage à Paris",
                "status": "brouillon",
                "date_creation": "2024-01-01T10:00:00",
                "date_modification": "2024-01-02T15:30:00"
            }
        }
