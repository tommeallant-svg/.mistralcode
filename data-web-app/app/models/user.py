"""
User model for authentication and authorization.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from .base import DBBase, Base


class User(DBBase):
    """
    User model for storing user information.
    For now, only one user: username='Paloma', password='laBest'
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # Store hashed passwords
    full_name = Column(String(100), nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships
    trips = relationship("Trip", back_populates="owner", cascade="all, delete-orphan")
    shared_trips = relationship("SharedTrip", foreign_keys="[SharedTrip.user_id]", back_populates="user", cascade="all, delete-orphan")
    shared_with_me = relationship("SharedTrip", foreign_keys="[SharedTrip.shared_with_user_id]", back_populates="shared_with_user", cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
