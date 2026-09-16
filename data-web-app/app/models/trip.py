"""
Trip model for managing travel trips.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Enum, func, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import DBBase


class TripStatus(str, PyEnum):
    """Status enum for trips"""
    DRAFT = "brouillon"
    VALIDATED = "validé"


class Trip(DBBase):
    """
    Trip model representing a travel journey.
    
    Attributes:
        name: Trip name
        start_date: Departure date
        end_date: Return date
        status: draft or validated
        latitude: GPS latitude
        longitude: GPS longitude
        description: Optional trip description
    """
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    status = Column(String(20), default=TripStatus.DRAFT, nullable=False)
    
    # GPS location (main point for the trip)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Foreign key to user
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="trips")
    steps = relationship("Step", back_populates="trip", cascade="all, delete-orphan", order_by="Step.order_index")
    shared_with = relationship("SharedTrip", back_populates="trip", cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Trip(id={self.id}, name='{self.name}', status={self.status})>"
