"""
Authentication API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from ..schemas.user import UserLogin, TokenResponse, UserResponse, MessageResponse
from ..services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


def get_auth_service():
    """Dependency for getting auth service"""
    return AuthService()


@router.post("/login", response_model=TokenResponse, summary="Login user")
async def login(
    request: UserLogin,
    service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate a user and return an access token.
    
    For demo purposes, use:
    - Username: Paloma
    - Password: laBest
    """
    await service.initialize()
    try:
        token = await service.create_access_token(
            request.username, 
            request.password
        )
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        user = await service.authenticate_user(request.username, request.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                email=user.email,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )
    finally:
        await service.shutdown()


@router.post("/logout", response_model=MessageResponse, summary="Logout user")
async def logout(
    request: Request
):
    """
    Logout user (clear token from client side).
    This endpoint is mainly for documentation as JWT tokens are stateless.
    """
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: AuthService = Depends(get_auth_service)
):
    """Get the current authenticated user"""
    await service.initialize()
    try:
        token = credentials.credentials
        user = await service.get_current_user(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return UserResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    finally:
        await service.shutdown()


@router.post("/verify", response_model=MessageResponse, summary="Verify token")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: AuthService = Depends(get_auth_service)
):
    """Verify if the current token is valid"""
    await service.initialize()
    try:
        token = credentials.credentials
        is_valid = await service.verify_token(token)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return MessageResponse(message="Token is valid")
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    finally:
        await service.shutdown()
