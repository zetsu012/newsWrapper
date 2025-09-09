import time
from typing import Dict, Optional
from collections import defaultdict, deque
from fastapi import HTTPException, Request
from config.settings import settings

class RateLimiter:
    def __init__(self):
        self.requests_per_period = settings.rate_limit_requests
        self.period_seconds = settings.rate_limit_period
        self.client_requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limit"""
        current_time = time.time()
        client_queue = self.client_requests[client_id]
        
        # Remove old requests outside the time window
        while client_queue and client_queue[0] <= current_time - self.period_seconds:
            client_queue.popleft()
        
        # Check if client has exceeded rate limit
        if len(client_queue) >= self.requests_per_period:
            return False
        
        # Add current request timestamp
        client_queue.append(current_time)
        return True
    
    def get_client_id(self, request: Request) -> str:
        """Extract client identifier from request"""
        # Try to get real IP if behind proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Try other proxy headers
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get number of requests remaining for client"""
        current_time = time.time()
        client_queue = self.client_requests[client_id]
        
        # Remove old requests
        while client_queue and client_queue[0] <= current_time - self.period_seconds:
            client_queue.popleft()
        
        return max(0, self.requests_per_period - len(client_queue))
    
    def get_reset_time(self, client_id: str) -> Optional[float]:
        """Get when the rate limit resets for client"""
        client_queue = self.client_requests[client_id]
        if not client_queue:
            return None
        
        return client_queue[0] + self.period_seconds
    
    def cleanup_old_entries(self, max_age_seconds: int = 3600):
        """Clean up old client entries to prevent memory leaks"""
        current_time = time.time()
        
        # Remove clients that haven't made requests recently
        clients_to_remove = []
        for client_id, queue in self.client_requests.items():
            if not queue or queue[-1] <= current_time - max_age_seconds:
                clients_to_remove.append(client_id)
        
        for client_id in clients_to_remove:
            del self.client_requests[client_id]

# Global rate limiter instance
rate_limiter = RateLimiter()

def apply_rate_limit(request: Request):
    """FastAPI dependency to apply rate limiting"""
    client_id = rate_limiter.get_client_id(request)
    
    if not rate_limiter.is_allowed(client_id):
        remaining = rate_limiter.get_remaining_requests(client_id)
        reset_time = rate_limiter.get_reset_time(client_id)
        
        headers = {
            "X-RateLimit-Limit": str(rate_limiter.requests_per_period),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(reset_time)) if reset_time else "0"
        }
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {rate_limiter.requests_per_period} per {rate_limiter.period_seconds} seconds",
                "retry_after": int(reset_time - time.time()) if reset_time else 0
            },
            headers=headers
        )
    
    return True
