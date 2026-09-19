"""
Step model for individual steps within a trip.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Enum, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import DBBase


class StepCategory(str, PyEnum):
    """Category enum for steps"""
    TRANSPORT = "transport"
    ACCOMMODATION = "hébergement"
    ACTIVITY = "activité"
    FOOD = "food"
    SPORT = "sport"
    HOBBIES = "hobbies"


class TransportType(str, PyEnum):
    """Transport type enum"""
    BOAT = "bateau"
    TRAIN = "train"
    PLANE = "avion"
    CAR = "voiture"
    SCOOTER = "scoot"
    BIKE = "vélo"
    WALK = "marche"
    BUS = "bus"


class Step(DBBase):
    """
    Step model representing an individual step in a trip.
    
    Attributes:
        name: Step name
        category: transport, hébergement, activité, food, sport, hobbies
        type: Specific type (especially for transport)
        start_datetime: Start date and time
        end_datetime: End date and time
        location_start: Starting location name
        location_end: Ending location name
        latitude_start: Starting GPS latitude
        longitude_start: Starting GPS longitude
        latitude_end: Ending GPS latitude
        longitude_end: Ending GPS longitude
        notes: Additional notes
        order_index: Order within the trip
    """
    __tablename__ = "steps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(20), nullable=False)
    type = Column(String(50), nullable=True)  # Can be TransportType values or other strings
    
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True), nullable=True)
    
    location_start = Column(String(200), nullable=True)
    location_end = Column(String(200), nullable=True)
    
    latitude_start = Column(Float, nullable=True)
    longitude_start = Column(Float, nullable=True)
    latitude_end = Column(Float, nullable=True)
    longitude_end = Column(Float, nullable=True)
    
    notes = Column(Text, nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    
    # Color for display (can be auto-generated based on category)
    color = Column(String(20), nullable=True)
    
    # Foreign key to trip
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    trip = relationship("Trip", back_populates="steps")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Step(id={self.id}, name='{self.name}', category={self.category}, order={self.order_index})>"
