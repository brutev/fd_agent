"""Rate limiting middleware"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

from config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit = settings.RATE_LIMIT_PER_MINUTE
        self.window = 60  # 1 minute window
        self.requests = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        
        async with self._lock:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.window)
            
            # Clean old requests
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if req_time > window_start
            ]
            
            # Check rate limit
            if len(self.requests[client_ip]) >= self.rate_limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Maximum {self.rate_limit} requests per minute allowed",
                        "retry_after": self.window
                    }
                )
            
            # Record this request
            self.requests[client_ip].append(now)
        
        response = await call_next(request)
        return response
