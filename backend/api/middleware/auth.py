"""Authentication middleware"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from jose import jwt, JWTError
from typing import Optional

from config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    """JWT Authentication middleware"""
    
    # Paths that don't require authentication
    PUBLIC_PATHS = [
        "/docs",
        "/redoc", 
        "/openapi.json",
        "/api/v1/auth/send-otp",
        "/api/v1/auth/verify-otp",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh-token",
        "/health",
        "/"
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public paths
        if any(request.url.path.startswith(path) for path in self.PUBLIC_PATHS):
            return await call_next(request)
        
        # Get token from header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Missing or invalid authorization header"
                }
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # Verify token
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            # Add user info to request state
            request.state.user_id = payload.get("sub")
            request.state.user = payload
            
        except JWTError as e:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Unauthorized",
                    "message": "Invalid or expired token"
                }
            )
        
        return await call_next(request)


def get_current_user(request: Request) -> dict:
    """Dependency to get current user from request state"""
    if hasattr(request.state, 'user'):
        return request.state.user
    return None
