from fastapi import Request
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class RateLimitStore:
    """In-memory store for rate limiting. In production, use Redis."""
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def is_allowed(self, identifier: str, max_requests: int = 5, window_seconds: int = 300) -> bool:
        """
        Check if a request is allowed based on rate limit.
        
        Args:
            identifier: IP address or email
            max_requests: Max requests allowed in the window
            window_seconds: Time window in seconds
        
        Returns:
            True if allowed, False if rate limited
        """
        async with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=window_seconds)
            
            # Remove old requests outside the window
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > cutoff
            ]
            
            # Check if limit exceeded
            if len(self.requests[identifier]) >= max_requests:
                return False
            
            # Add current request
            self.requests[identifier].append(now)
            return True

# Global rate limit store
rate_limit_store = RateLimitStore()

async def rate_limit(request: Request, max_requests: int = 5, window_seconds: int = 300) -> bool:
    """
    Rate limit middleware for login/registration endpoints.
    Uses IP address as identifier.
    """
    client_ip = request.client.host if request.client else "unknown"
    return await rate_limit_store.is_allowed(client_ip, max_requests, window_seconds)

async def rate_limit_by_email(email: str, max_requests: int = 3, window_seconds: int = 600) -> bool:
    """
    Rate limit by email for password reset requests.
    Max 3 attempts per email in 10 minutes.
    """
    return await rate_limit_store.is_allowed(email, max_requests, window_seconds)