"""
AI service for the conversational agent.
"""

import logging
import json
import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import httpx

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..config import settings
from ..schemas.ai import (
    AIMessage, AIChatRequest, AIChatResponse, AIResponse, AIProposal
)
from ..repositories.trip_repository import TripRepository
from ..repositories.step_repository import StepRepository

logger = logging.getLogger(__name__)

# Mistral AI API configuration
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = "mistral-api-key"  # To be configured

# Google Maps API
GOOGLE_MAPS_API_KEY = "google-maps-api-key"  # To be configured
GOOGLE_MAPS_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
GOOGLE_MAPS_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


class AIService:
    """Service for AI chat operations"""
    
    def __init__(self):
        self.engine = None
        self.session_maker = None
        self._initialized = False
        self._mistral_client = httpx.AsyncClient()
        self._google_client = httpx.AsyncClient()
        
        # Conversation history storage (in memory for now)
        self._conversations: Dict[int, List[AIMessage]] = {}
    
    async def initialize(self):
        """Initialize the service"""
        if self._initialized:
            return
        
        self._initialized = True
    
    async def shutdown(self):
        """Shutdown the service"""
        await self._mistral_client.aclose()
        await self._google_client.aclose()
        self._initialized = False
    
    async def _get_session(self) -> AsyncSession:
        """Get a database session"""
        if not self._initialized:
            await self.initialize()
        
        if not self.engine:
            database_url = settings.database.database_url
            self.engine = create_async_engine(
                database_url,
                pool_size=settings.database.db_pool_size,
                max_overflow=settings.database.db_max_overflow,
                echo=False
            )
            self.session_maker = sessionmaker(
                self.engine,
                expire_on_commit=False,
                class_=AsyncSession
            )
        
        return self.session_maker()
    
    def _parse_ai_proposals(self, text: str) -> List[AIProposal]:
        """Parse AI text response to extract proposals"""
        proposals = []
        
        # Try to parse JSON proposals
        json_pattern = r'\{[^{}]*\}'
        json_matches = re.findall(json_pattern, text)
        
        for match in json_matches:
            try:
                data = json.loads(match)
                if isinstance(data, dict):
                    proposals.append(AIProposal(**data))
            except:
                continue
        
        # If no JSON found, try to parse text proposals
        if not proposals:
            # Simple text parsing
            lines = text.split('\n')
            current_proposal = {}
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('Nom:'):
                    current_proposal['name'] = line[5:].strip()
                elif line.startswith('Catégorie:'):
                    current_proposal['category'] = line[11:].strip()
                elif line.startswith('Type:'):
                    current_proposal['type'] = line[6:].strip()
                elif line.startswith('Description:'):
                    current_proposal['description'] = line[13:].strip()
                elif line.startswith('Lieu:'):
                    current_proposal['location_start'] = line[6:].strip()
                elif line.startswith('Date:'):
                    current_proposal['start_datetime'] = line[6:].strip()
                elif 'http' in line and ('google.com/maps' in line or 'maps.google.com' in line):
                    current_proposal['google_maps_link'] = line.strip()
                elif line.startswith('---') or line.startswith('==='):
                    if current_proposal:
                        proposals.append(AIProposal(**current_proposal))
                        current_proposal = {}
            
            if current_proposal:
                proposals.append(AIProposal(**current_proposal))
        
        return proposals
    
    async def chat(self, user_id: int, request: AIChatRequest) -> AIChatResponse:
        """Handle AI chat request"""
        await self.initialize()
        
        # Get trip context
        async with await self._get_session() as session:
            trip_repo = TripRepository(session)
            trip = await trip_repo.get_by_id_with_access_check(request.trip_id, user_id)
            
            if not trip:
                return AIChatResponse(
                    success=False,
                    response=AIResponse(
                        message="Trip not found or no access",
                        proposals=[],
                        sources=[]
                    ),
                    history=[]
                )
            
            # Get steps for context
            step_repo = StepRepository(session)
            steps = await step_repo.list_by_trip(trip.id)
        
        # Build context message
        context_parts = [
            f"Tu es un assistant voyage qui aide à planifier des voyages.",
            f"Le voyage actuel s'appelle '{trip.name}'.",
            f"Dates: du {trip.start_date} au {trip.end_date}",
            f"Statut: {trip.status}",
        ]
        
        if steps:
            context_parts.append("Étapes existantes:")
            for step in steps:
                context_parts.append(f"  - {step.name} ({step.category})")
        
        context = "\n".join(context_parts)
        
        # Build messages for AI
        messages = [
            {
                "role": "system",
                "content": """Tu es un assistant IA spécialisé dans la planification de voyages (road app). 
Tu aides l'utilisateur à trouver des activités, hébergements, transports, restaurants, etc. pour son voyage.

Quand tu fais des propositions, utilise le format suivant pour chaque proposition:
{
    "name": "Nom de l'étape",
    "category": "catégorie parmi: transport, hébergement, activité, food, sport, hobbies",
    "type": "type spécifique (pour transport: bateau, train, avion, voiture, scoot, vélo, marche, bus)",
    "description": "description détaillée",
    "start_datetime": "date/heure de début",
    "end_datetime": "date/heure de fin",
    "location_start": "lieu de départ",
    "location_end": "lieu d'arrivée",
    "google_maps_link": "lien Google Maps"
}

Si tu fais une recherche web, fournis les liens trouvés dans un tableau sources.
Toujours répondre en français."""
            },
            {
                "role": "user",
                "content": context
            },
            {
                "role": "user",
                "content": request.message
            }
        ]
        
        # Add conversation history
        conversation_id = request.trip_id  # Use trip_id as conversation ID
        if request.history:
            for msg in request.history:
                messages.append({"role": msg.role, "content": msg.content})
        
        # Call Mistral API
        try:
            # For now, return a mock response (replace with actual API call)
            ai_message = f"Je vais t'aider avec ta demande: {request.message}"
            
            # Generate mock proposals based on message
            proposals = []
            if "restaurant" in request.message.lower():
                proposals.append(AIProposal(
                    name="Dîner au restaurant Le Bistro",
                    category="food",
                    description="Restaurant français typique",
                    location_start="10 Rue de Paris",
                    google_maps_link="https://www.google.com/maps?q=10+Rue+de+Paris"
                ))
            elif "musée" in request.message.lower():
                proposals.append(AIProposal(
                    name="Visite du Musée",
                    category="activité",
                    description="Musée d'art moderne",
                    location_start="Place de la Culture",
                    google_maps_link="https://www.google.com/maps?q=Place+de+la+Culture"
                ))
            elif "train" in request.message.lower():
                proposals.append(AIProposal(
                    name="Trajet en train",
                    category="transport",
                    type="train",
                    description="Trajet Paris-Lyon",
                    location_start="Paris Gare de Lyon",
                    location_end="Lyon Part-Dieu",
                    google_maps_link="https://www.google.com/maps?q=Paris+Gare+de+Lyon"
                ))
            
            # Save to conversation history
            new_message = AIMessage(
                role="user",
                content=request.message,
                timestamp=datetime.utcnow()
            )
            
            if conversation_id not in self._conversations:
                self._conversations[conversation_id] = []
            
            self._conversations[conversation_id].append(new_message)
            
            response = AIChatResponse(
                success=True,
                response=AIResponse(
                    message=ai_message,
                    proposals=proposals,
                    sources=[{"url": "https://www.google.com", "title": "Exemple"}],
                    timestamp=datetime.utcnow()
                ),
                history=self._conversations[conversation_id] + [
                    AIMessage(
                        role="assistant",
                        content=ai_message,
                        timestamp=datetime.utcnow()
                    )
                ]
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            return AIChatResponse(
                success=False,
                response=AIResponse(
                    message=f"Erreur: {str(e)}",
                    proposals=[],
                    sources=[]
                ),
                history=request.history or []
            )
    
    async def search_web(self, query: str) -> List[Dict[str, Any]]:
        """Search the web for information"""
        # Mock implementation - replace with actual web search
        return [
            {
                "title": f"Résultat pour: {query}",
                "url": f"https://www.google.com/search?q={query}",
                "snippet": "Description du résultat"
            }
        ]
    
    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """Geocode an address using Google Maps API"""
        # Mock implementation
        # In production, call Google Maps Geocoding API
        import random
        return {
            "lat": random.uniform(-90, 90),
            "lng": random.uniform(-180, 180),
            "formatted_address": address
        }
    
    async def add_proposal_as_step(self, user_id: int, trip_id: int, 
                                   proposal_index: int, override_data: Optional[Dict] = None) -> bool:
        """Add an AI proposal as a step to a trip"""
        # Get the last chat response for this trip
        conversation_id = trip_id
        if conversation_id not in self._conversations or len(self._conversations[conversation_id]) < 2:
            return False
        
        # Get the last AI response
        last_assistant_msg = None
        for i in range(len(self._conversations[conversation_id]) - 1, -1, -1):
            if self._conversations[conversation_id][i].role == "assistant":
                last_assistant_msg = self._conversations[conversation_id][i]
                break
        
        if not last_assistant_msg:
            return False
        
        # Parse proposals from the message (this would be better stored with the message)
        # For now, return False - implementation would need to be enhanced
        return False
    
    async def get_conversation_history(self, trip_id: int) -> List[AIMessage]:
        """Get conversation history for a trip"""
        return self._conversations.get(trip_id, [])
    
    async def clear_conversation_history(self, trip_id: int) -> bool:
        """Clear conversation history for a trip"""
        if trip_id in self._conversations:
            del self._conversations[trip_id]
            return True
        return False
