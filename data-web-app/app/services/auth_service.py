"""
Authentication service for user authentication and token management.
"""

import logging
import hashlib
import secrets
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jwt import encode as jwt_encode, decode as jwt_decode, ExpiredSignatureError, InvalidTokenError

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..config import settings
from ..models.user import User
from ..repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

# Secret key for JWT (in production, use a proper secret from config)
SECRET_KEY = settings.app.secret_key or "road-secret-key-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days for demo purposes


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        self.engine = None
        self.session_maker = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the service with database connection"""
        if self._initialized:
            return
        
        from ..config import settings
        
        # Only initialize database if using postgres
        if settings.app.data_source == "postgres":
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
            self._initialized = True
        else:
            # For CSV mode, we don't need database
            self._initialized = True
    
    async def shutdown(self):
        """Shutdown the service"""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_maker = None
            self._initialized = False
    
    async def _get_session(self) -> Optional[AsyncSession]:
        """Get a database session"""
        await self.initialize()
        if self.session_maker:
            return self.session_maker()
        return None
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256 (for demo purposes)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self._hash_password(password) == hashed_password
    
    def _create_jwt_token(self, user_id: int, username: str) -> str:
        """Create a JWT token for a user"""
        payload = {
            "sub": str(user_id),
            "username": username,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        token = jwt_encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    
    def _decode_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify a JWT token"""
        try:
            payload = jwt_decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        # For demo: hardcoded user - can work without database
        if username == "Paloma" and password == "laBest":
            # Try to get or create the user from database if available
            try:
                session = await self._get_session()
                if session:
                    async with session as s:
                        repo = UserRepository(s)
                        user = await repo.get_by_username(username)
                        
                        if not user:
                            # Create the hardcoded user
                            user = await repo.get_hardcoded_user()
                        
                        return user
            except Exception as e:
                logger.warning(f"Could not connect to database for auth: {e}")
            
            # Return a mock user for demo purposes
            # In production, this should not happen
            from ..models.user import User as UserModel
            user = UserModel()
            user.id = 1
            user.username = "Paloma"
            user.full_name = "Paloma User"
            user.email = "paloma@example.com"
            user.is_active = True
            user.is_superuser = True
            return user
        
        # Try to authenticate with database users
        try:
            session = await self._get_session()
            if session:
                async with session as s:
                    repo = UserRepository(s)
                    user = await repo.get_by_username(username)
                    
                    if user and user.is_active and self._verify_password(password, user.password_hash):
                        return user
        except Exception as e:
            logger.warning(f"Database authentication failed: {e}")
        
        return None
    
    async def create_access_token(self, username: str, password: str) -> Optional[str]:
        """Create an access token for authenticated user"""
        user = await self.authenticate_user(username, password)
        if not user:
            return None
        
        token = self._create_jwt_token(user.id, user.username)
        return token
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get the current user from a JWT token"""
        payload = self._decode_jwt_token(token)
        if not payload:
            return None
        
        user_id = int(payload.get("sub", 0))
        username = payload.get("username", "")
        
        # For hardcoded demo user, return mock user if database unavailable
        if username == "Paloma" and user_id == 1:
            try:
                session = await self._get_session()
                if session:
                    async with session as s:
                        repo = UserRepository(s)
                        user = await repo.get_by_id(user_id)
                        return user
            except Exception as e:
                logger.warning(f"Could not connect to database for user lookup: {e}")
            
            # Return mock user for demo
            from ..models.user import User as UserModel
            user = UserModel()
            user.id = 1
            user.username = "Paloma"
            user.full_name = "Paloma User"
            user.email = "paloma@example.com"
            user.is_active = True
            user.is_superuser = True
            return user
        
        # Try to get user from database
        try:
            session = await self._get_session()
            if session:
                async with session as s:
                    repo = UserRepository(s)
                    user = await repo.get_by_id(user_id)
                    return user
        except Exception as e:
            logger.warning(f"Database user lookup failed: {e}")
        
        return None
    
    async def verify_token(self, token: str) -> bool:
        """Verify if a token is valid"""
        return self._decode_jwt_token(token) is not None
    
    async def get_token_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """Get the payload from a JWT token"""
        return self._decode_jwt_token(token)
