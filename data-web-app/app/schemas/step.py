"""
Pydantic schemas for Step model.
"""

from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from .trip import TripSummaryResponse


# Enums for categories and types
class StepCategory(str, Enum):
    TRANSPORT = "transport"
    ACCOMMODATION = "hébergement"
    ACTIVITY = "activité"
    FOOD = "food"
    SPORT = "sport"
    HOBBIES = "hobbies"


class TransportType(str, Enum):
    BOAT = "bateau"
    TRAIN = "train"
    PLANE = "avion"
    CAR = "voiture"
    SCOOTER = "scoot"
    BIKE = "vélo"
    WALK = "marche"
    BUS = "bus"


class StepBase(BaseModel):
    """Base step schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Step name")
    category: str = Field(..., description="Step category (transport/hébergement/activité/food/sport/hobbies)")
    type: Optional[str] = Field(default=None, max_length=50, description="Step type (for transport)")
    start_datetime: datetime = Field(..., description="Start date and time")
    end_datetime: Optional[datetime] = Field(default=None, description="End date and time")
    location_start: Optional[str] = Field(default=None, max_length=200, description="Starting location")
    location_end: Optional[str] = Field(default=None, max_length=200, description="Ending location")
    latitude_start: Optional[float] = Field(default=None, ge=-90, le=90, description="Start latitude")
    longitude_start: Optional[float] = Field(default=None, ge=-180, le=180, description="Start longitude")
    latitude_end: Optional[float] = Field(default=None, ge=-90, le=90, description="End latitude")
    longitude_end: Optional[float] = Field(default=None, ge=-180, le=180, description="End longitude")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    order_index: int = Field(default=0, description="Order within trip")
    color: Optional[str] = Field(default=None, max_length=20, description="Display color")


class StepCreate(StepBase):
    """Schema for creating a step"""
    trip_id: int = Field(..., description="Parent trip ID")


class StepUpdate(BaseModel):
    """Schema for updating a step"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    category: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None, max_length=50)
    start_datetime: Optional[datetime] = Field(default=None)
    end_datetime: Optional[datetime] = Field(default=None)
    location_start: Optional[str] = Field(default=None, max_length=200)
    location_end: Optional[str] = Field(default=None, max_length=200)
    latitude_start: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude_start: Optional[float] = Field(default=None, ge=-180, le=180)
    latitude_end: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude_end: Optional[float] = Field(default=None, ge=-180, le=180)
    notes: Optional[str] = Field(default=None)
    order_index: Optional[int] = Field(default=None)
    color: Optional[str] = Field(default=None, max_length=20)


class StepResponse(StepBase):
    """Full step response schema"""
    id: int = Field(..., description="Step ID")
    trip_id: int = Field(..., description="Parent trip ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    class Config:
        from_attributes = True


class StepListResponse(BaseModel):
    """Response schema for listing steps"""
    steps: List[StepResponse] = Field(default_factory=list, description="List of steps")
    total: int = Field(default=0, description="Total number of steps")
    trip_id: int = Field(..., description="Parent trip ID")


class StepReorderRequest(BaseModel):
    """Schema for reordering steps"""
    step_ids: List[int] = Field(..., description="List of step IDs in new order")


class StepTableRow(BaseModel):
    """Schema for step table row (for frontend table display)"""
    id: int = Field(..., description="Step ID")
    name: str = Field(..., description="Step name")
    category: str = Field(..., description="Category")
    type: Optional[str] = Field(default=None, description="Type")
    start_datetime: datetime = Field(..., description="Start date/time")
    end_datetime: Optional[datetime] = Field(default=None, description="End date/time")
    location_start: Optional[str] = Field(default=None, description="Start location")
    location_end: Optional[str] = Field(default=None, description="End location")
    order_index: int = Field(default=0, description="Order")
    color: Optional[str] = Field(default=None, description="Color")
    
    class Config:
        from_attributes = True
