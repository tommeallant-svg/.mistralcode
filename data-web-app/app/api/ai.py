"""
AI API routes for the conversational agent.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import logging
import json

from ..schemas.ai import (
    AIChatRequest, AIChatResponse, AIMessage, AIProposal, AIAddStepRequest
)
from ..schemas.user import MessageResponse
from ..services.ai_service import AIService
from ..services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

logger = logging.getLogger(__name__)

security = HTTPBearer()


def get_ai_service():
    """Dependency for getting AI service"""
    return AIService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from token"""
    service = AuthService()
    await service.initialize()
    try:
        token = credentials.credentials
        user = await service.get_current_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user.id
    finally:
        await service.shutdown()


@router.post("/chat", response_model=AIChatResponse, summary="Chat with AI agent")
async def chat_with_ai(
    request: AIChatRequest,
    user_id: int = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """
    Chat with the AI travel assistant.
    
    The AI can help plan your trip, suggest activities, find accommodations,
    and provide Google Maps links for locations.
    """
    await service.initialize()
    try:
        response = await service.chat(user_id, request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/conversation/{trip_id}", response_model=List[AIMessage], summary="Get conversation history")
async def get_conversation_history(
    trip_id: int,
    user_id: int = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """Get conversation history for a trip"""
    await service.initialize()
    try:
        # Verify user has access to the trip
        from ..services.trip_service import TripService
        trip_service = TripService()
        await trip_service.initialize()
        trip = await trip_service.get_trip(trip_id, user_id)
        await trip_service.shutdown()
        
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found or no access")
        
        return await service.get_conversation_history(trip_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.delete("/conversation/{trip_id}", response_model=MessageResponse, summary="Clear conversation history")
async def clear_conversation_history(
    trip_id: int,
    user_id: int = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """Clear conversation history for a trip"""
    await service.initialize()
    try:
        # Verify user has access to the trip
        from ..services.trip_service import TripService
        trip_service = TripService()
        await trip_service.initialize()
        trip = await trip_service.get_trip(trip_id, user_id)
        await trip_service.shutdown()
        
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found or no access")
        
        success = await service.clear_conversation_history(trip_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return MessageResponse(message="Conversation history cleared")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.post("/proposal", response_model=MessageResponse, summary="Add AI proposal as step")
async def add_proposal_as_step(
    request: AIAddStepRequest,
    user_id: int = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """Add an AI proposal as a new step to a trip"""
    await service.initialize()
    try:
        # Verify user has access to the trip
        from ..services.trip_service import TripService
        trip_service = TripService()
        await trip_service.initialize()
        trip = await trip_service.get_trip(request.trip_id, user_id)
        await trip_service.shutdown()
        
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found or no access")
        
        success = await service.add_proposal_as_step(
            user_id, 
            request.trip_id, 
            request.proposal_index,
            request.override_data
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        return MessageResponse(message="Proposal added as step")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding proposal as step: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/proposals/suggestions", summary="Get AI suggestions for a trip")
async def get_ai_suggestions(
    trip_id: int = Query(..., description="Trip ID"),
    query: Optional[str] = Query(default=None, description="Search query for suggestions"),
    user_id: int = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """
    Get AI suggestions for a trip based on current steps and user query.
    
    This endpoint provides intelligent suggestions for new steps to add to a trip.
    """
    await service.initialize()
    try:
        # Get trip context
        from ..services.trip_service import TripService
        trip_service = TripService()
        await trip_service.initialize()
        
        trip = await trip_service.get_trip(trip_id, user_id)
        if not trip:
            await trip_service.shutdown()
            raise HTTPException(status_code=404, detail="Trip not found or no access")
        
        map_data = await trip_service.get_trip_map_data(trip_id, user_id)
        await trip_service.shutdown()
        
        # Generate suggestions based on current trip data
        suggestions = []
        
        # If query provided, use it
        if query:
            # Mock suggestions based on query
            query_lower = query.lower()
            
            if "restaurant" in query_lower or "manger" in query_lower or "food" in query_lower:
                suggestions.append(AIProposal(
                    name="Découverte culinaire",
                    category="food",
                    description=f"Trouver des restaurants pour: {query}",
                    google_maps_link="https://www.google.com/maps/search/restaurants"
                ))
            
            if "musée" in query_lower or "culture" in query_lower or "visite" in query_lower:
                suggestions.append(AIProposal(
                    name="Visite culturelle",
                    category="activité",
                    description=f"Visiter des lieux culturels: {query}",
                    google_maps_link="https://www.google.com/maps/search/musees"
                ))
            
            if "train" in query_lower or "transport" in query_lower:
                suggestions.append(AIProposal(
                    name="Trajet en transport",
                    category="transport",
                    type="train",
                    description=f"Organiser un trajet: {query}",
                    google_maps_link="https://www.google.com/maps"
                ))
            
            if "hôtel" in query_lower or "hébergement" in query_lower or "dormir" in query_lower:
                suggestions.append(AIProposal(
                    name="Hébergement",
                    category="hébergement",
                    description=f"Trouver un hébergement: {query}",
                    google_maps_link="https://www.google.com/maps/search/hotels"
                ))
        else:
            # Generic suggestions based on trip
            if trip.steps_count == 0:
                suggestions.extend([
                    AIProposal(
                        name="Ajouter un transport",
                        category="transport",
                        type="avion",
                        description="Ajouter un moyen de transport pour commencer votre voyage",
                        google_maps_link="https://www.google.com/maps"
                    ),
                    AIProposal(
                        name="Ajouter un hébergement",
                        category="hébergement",
                        description="Ajouter un lieu d'hébergement",
                        google_maps_link="https://www.google.com/maps/search/hotels"
                    ),
                    AIProposal(
                        name="Ajouter une activité",
                        category="activité",
                        description="Ajouter une activité touristique",
                        google_maps_link="https://www.google.com/maps/search/attractions"
                    )
                ])
        
        return {"suggestions": suggestions, "trip_name": trip.name, "trip_id": trip.id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting AI suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()
