"""
SharedTrip model for sharing trips between users.
"""

from sqlalchemy import Column, Integer, DateTime, func, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from .base import DBBase


class SharedTrip(DBBase):
    """
    Model for sharing trips between users.
    
    When a user shares a trip with another user, 
    the other user can view (and potentially edit) the trip.
    """
    __tablename__ = "shared_trips"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User who owns the trip
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # User with whom the trip is shared
    shared_with_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # The trip being shared
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    
    # Permissions
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="shared_trips")
    shared_with_user = relationship("User", foreign_keys=[shared_with_user_id], back_populates="shared_with_me")
    trip = relationship("Trip", back_populates="shared_with")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SharedTrip(id={self.id}, trip_id={self.trip_id}, from={self.user_id}, to={self.shared_with_user_id})>"
