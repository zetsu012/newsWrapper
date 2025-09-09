import json
import redis
from typing import Optional, Any
from datetime import datetime, timedelta
from config.settings import settings

class CacheManager:
    def __init__(self):
        self.enabled = settings.enable_cache
        self.ttl = settings.cache_ttl
        self.redis_client = None
        
        if self.enabled:
            try:
                self.redis_client = redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    password=settings.redis_password,
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
            except Exception as e:
                print(f"Redis connection failed, disabling cache: {e}")
                self.enabled = False
                self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value by key"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"Cache get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value with optional TTL"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            cache_ttl = ttl or self.ttl
            serialized_value = json.dumps(value, default=self._json_serializer)
            self.redis_client.setex(key, cache_ttl, serialized_value)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cached values"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a cache key from prefix and parameters"""
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)

# Global cache manager instance
cache_manager = CacheManager()
