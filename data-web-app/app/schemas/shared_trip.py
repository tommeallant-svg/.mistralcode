"""
Pydantic schemas for SharedTrip model.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from .user import UserResponse
from .trip import TripSummaryResponse


class SharedTripBase(BaseModel):
    """Base shared trip schema"""
    can_edit: bool = Field(default=False, description="Can edit the shared trip")
    can_delete: bool = Field(default=False, description="Can delete the shared trip")


class SharedTripCreate(SharedTripBase):
    """Schema for creating a shared trip"""
    user_id: int = Field(..., description="User ID who owns the trip")
    shared_with_user_id: int = Field(..., description="User ID with whom to share")
    trip_id: int = Field(..., description="Trip ID to share")


class SharedTripResponse(SharedTripBase):
    """Full shared trip response schema"""
    id: int = Field(..., description="Shared trip ID")
    user_id: int = Field(..., description="User ID who owns the trip")
    shared_with_user_id: int = Field(..., description="User ID with whom shared")
    trip_id: int = Field(..., description="Trip ID")
    user: Optional[UserResponse] = Field(default=None, description="Owner user")
    shared_with_user: Optional[UserResponse] = Field(default=None, description="Shared with user")
    trip: Optional[TripSummaryResponse] = Field(default=None, description="Shared trip")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    class Config:
        from_attributes = True


class SharedTripListResponse(BaseModel):
    """Response schema for listing shared trips"""
    shared_trips: List[SharedTripResponse] = Field(default_factory=list, description="List of shared trips")
    total: int = Field(default=0, description="Total number of shared trips")
