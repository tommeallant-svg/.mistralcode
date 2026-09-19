"""
Pydantic schemas for AI agent interactions.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AIMessage(BaseModel):
    """Schema for AI chat message"""
    role: str = Field(..., description="Role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")


class AIChatRequest(BaseModel):
    """Schema for AI chat request"""
    trip_id: int = Field(..., description="Trip ID for context")
    message: str = Field(..., description="User message")
    history: Optional[List[AIMessage]] = Field(default=None, description="Previous messages in conversation")


class AIProposal(BaseModel):
    """Schema for AI proposal (suggestion for a new step)"""
    name: str = Field(..., description="Proposed step name")
    category: str = Field(..., description="Proposed category")
    type: Optional[str] = Field(default=None, description="Proposed type")
    description: Optional[str] = Field(default=None, description="Description")
    start_datetime: Optional[str] = Field(default=None, description="Proposed start datetime")
    end_datetime: Optional[str] = Field(default=None, description="Proposed end datetime")
    location_start: Optional[str] = Field(default=None, description="Proposed start location")
    location_end: Optional[str] = Field(default=None, description="Proposed end location")
    latitude: Optional[float] = Field(default=None, description="Latitude")
    longitude: Optional[float] = Field(default=None, description="Longitude")
    google_maps_link: Optional[str] = Field(default=None, description="Google Maps link")
    confidence: float = Field(default=0.0, description="AI confidence score")


class AIResponse(BaseModel):
    """Schema for AI response"""
    message: str = Field(..., description="AI response message")
    proposals: List[AIProposal] = Field(default_factory=list, description="List of proposals")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="List of sources/links")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class AIChatResponse(BaseModel):
    """Full AI chat response schema"""
    success: bool = Field(..., description="Whether the request was successful")
    response: AIResponse = Field(..., description="AI response")
    history: List[AIMessage] = Field(default_factory=list, description="Updated conversation history")


class AIAddStepRequest(BaseModel):
    """Schema for adding a step from AI proposal"""
    trip_id: int = Field(..., description="Trip ID")
    proposal_index: int = Field(..., description="Index of proposal to add")
    override_data: Optional[Dict[str, Any]] = Field(default=None, description="Data to override in proposal")
