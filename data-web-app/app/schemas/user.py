"""
Pydantic schemas for User model.
"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=1, max_length=50, description="Username")
    full_name: Optional[str] = Field(default=None, max_length=100, description="Full name")
    email: Optional[EmailStr] = Field(default=None, description="Email address")
    is_active: bool = Field(default=True, description="Whether user is active")
    is_superuser: bool = Field(default=False, description="Whether user is superuser")


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8, description="Password")


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    username: Optional[str] = Field(default=None, min_length=1, max_length=50)
    full_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None, min_length=8)
    is_active: Optional[bool] = Field(default=None)
    is_superuser: Optional[bool] = Field(default=None)


class UserResponse(UserBase):
    """User response schema"""
    id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="User information")


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str = Field(..., description="Message")
