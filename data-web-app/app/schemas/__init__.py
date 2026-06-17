"""
Pydantic schemas for request/response validation.
"""

from .dataset import (
    DatasetResponse,
    DatasetListResponse,
    DatasetCreateResponse,
    DatasetQueryResponse,
    ErrorResponse,
    HealthResponse
)
from .user import UserBase, UserCreate, UserUpdate, UserResponse, UserLogin, TokenResponse, MessageResponse
from .trip import TripBase, TripCreate, TripUpdate, TripResponse, TripListResponse, TripSummaryResponse, TripTableRow
from .step import StepCategory, TransportType, StepBase, StepCreate, StepUpdate, StepResponse, StepListResponse, StepTableRow, StepReorderRequest

# Rebuild models to resolve forward references
TripResponse.model_rebuild()
from .shared_trip import SharedTripBase, SharedTripCreate, SharedTripResponse, SharedTripListResponse
from .ai import AIMessage, AIChatRequest, AIChatResponse, AIResponse, AIProposal, AIAddStepRequest

__all__ = [
    # Dataset schemas
    "DatasetResponse",
    "DatasetListResponse",
    "DatasetCreateResponse",
    "DatasetQueryResponse",
    "ErrorResponse",
    "HealthResponse",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "TokenResponse",
    "MessageResponse",
    # Trip schemas
    "TripBase",
    "TripCreate",
    "TripUpdate",
    "TripResponse",
    "TripListResponse",
    "TripSummaryResponse",
    "TripTableRow",
    # Step schemas
    "StepCategory",
    "TransportType",
    "StepBase",
    "StepCreate",
    "StepUpdate",
    "StepResponse",
    "StepListResponse",
    "StepTableRow",
    "StepReorderRequest",
    # Shared trip schemas
    "SharedTripBase",
    "SharedTripCreate",
    "SharedTripResponse",
    "SharedTripListResponse",
    # AI schemas
    "AIMessage",
    "AIChatRequest",
    "AIChatResponse",
    "AIResponse",
    "AIProposal",
    "AIAddStepRequest"
]
