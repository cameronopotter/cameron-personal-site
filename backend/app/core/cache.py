"""
In-memory caching layer for Digital Greenhouse API
"""

import asyncio
import json
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import logging
import fnmatch

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheItem:
    """Cache item with TTL support"""
    def __init__(self, value: Any, ttl_seconds: Optional[int] = None):
        self.value = value
        self.created_at = datetime.now()
        self.expires_at = None
        if ttl_seconds:
            self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        """Check if cache item is expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class InMemoryCacheManager:
    """In-memory cache manager with TTL support"""
    
    def __init__(self):
        self._cache: Dict[str, CacheItem] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self):
        """Initialize cache (no-op for in-memory)"""
        logger.info("In-memory cache initialized")
    
    async def disconnect(self):
        """Close cache (no-op for in-memory)"""
        async with self._lock:
            self._cache.clear()
        logger.info("In-memory cache cleared")
    
    async def _cleanup_expired(self):
        """Clean up expired cache items"""
        current_time = datetime.now()
        expired_keys = [
            key for key, item in self._cache.items()
            if item.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            await self._cleanup_expired()
            
            item = self._cache.get(key)
            if item is None or item.is_expired():
                return None
            
            return item.value
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL"""
        async with self._lock:
            self._cache[key] = CacheItem(value, ttl_seconds)
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        async with self._lock:
            await self._cleanup_expired()
            item = self._cache.get(key)
            return item is not None and not item.is_expired()
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        async with self._lock:
            # Convert Redis-style pattern to fnmatch pattern
            fnmatch_pattern = pattern.replace("*", "*")
            
            matching_keys = [
                key for key in self._cache.keys()
                if fnmatch.fnmatch(key, fnmatch_pattern)
            ]
            
            for key in matching_keys:
                del self._cache[key]
            
            return len(matching_keys)
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value"""
        async with self._lock:
            item = self._cache.get(key)
            if item is None or item.is_expired():
                new_value = amount
            else:
                try:
                    current_value = int(item.value)
                    new_value = current_value + amount
                except (ValueError, TypeError):
                    return None
            
            self._cache[key] = CacheItem(new_value, None)
            return new_value
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        async with self._lock:
            await self._cleanup_expired()
            return {
                "total_keys": len(self._cache),
                "memory_usage_items": len(self._cache)
            }


# Cache TTL configurations
class CacheTTL:
    """Cache TTL constants for different data types"""
    
    # Frequently accessed data
    GARDEN_STATE = 300  # 5 minutes
    WEATHER_STATE = 900  # 15 minutes
    PROJECT_DETAILS = 1800  # 30 minutes
    SKILLS_CONSTELLATION = 3600  # 1 hour
    
    # Analytics data
    ANALYTICS_DASHBOARD = 3600  # 1 hour
    REALTIME_METRICS = 60  # 1 minute
    VISITOR_ANALYTICS = 1800  # 30 minutes
    
    # External API data
    GITHUB_DATA = 1800  # 30 minutes
    SPOTIFY_DATA = 300  # 5 minutes
    WEATHER_API_DATA = 1800  # 30 minutes
    
    # Session data
    VISITOR_SESSION = 3600  # 1 hour
    RATE_LIMIT = 3600  # 1 hour
    
    # Background task results
    GROWTH_CALCULATION = 900  # 15 minutes
    DATA_SYNC_STATUS = 1800  # 30 minutes


# Cache key generators
class CacheKeys:
    """Cache key generators for consistent naming"""
    
    @staticmethod
    def garden_state(season: str = "", weather: str = "", visitor_hash: str = "") -> str:
        return f"garden:state:{season}:{weather}:{visitor_hash}"
    
    @staticmethod
    def project_details(project_id: str) -> str:
        return f"project:details:{project_id}"
    
    @staticmethod
    def project_analytics(project_id: str) -> str:
        return f"project:analytics:{project_id}"
    
    @staticmethod
    def skills_constellation() -> str:
        return "skills:constellation:all"
    
    @staticmethod
    def weather_current() -> str:
        return "weather:current"
    
    @staticmethod
    def analytics_dashboard(date_range: str) -> str:
        return f"analytics:dashboard:{date_range}"
    
    @staticmethod
    def realtime_metrics() -> str:
        return "analytics:realtime"
    
    @staticmethod
    def visitor_session(session_token: str) -> str:
        return f"visitor:session:{session_token}"
    
    @staticmethod
    def github_repo_data(repo: str) -> str:
        return f"github:repo:{repo}"
    
    @staticmethod
    def spotify_current() -> str:
        return "spotify:current"
    
    @staticmethod
    def weather_api_data(location: str) -> str:
        return f"weather:api:{location}"
    
    @staticmethod
    def rate_limit(identifier: str, endpoint: str) -> str:
        return f"rate_limit:{identifier}:{endpoint}"
    
    @staticmethod
    def growth_calculation(project_id: str) -> str:
        return f"growth:calculation:{project_id}"
    
    @staticmethod
    def data_sync_status(source: str) -> str:
        return f"sync:status:{source}"


# Global cache manager instance
cache_manager = InMemoryCacheManager()


# Convenience functions
async def get_cached(key: str) -> Optional[Any]:
    """Get value from cache"""
    return await cache_manager.get(key)


async def set_cached(
    key: str, 
    value: Any, 
    ttl_seconds: Optional[int] = None
) -> bool:
    """Set value in cache"""
    return await cache_manager.set(key, value, ttl_seconds)


async def delete_cached(key: str) -> bool:
    """Delete value from cache"""
    return await cache_manager.delete(key)


async def cached_exists(key: str) -> bool:
    """Check if key exists in cache"""
    return await cache_manager.exists(key)


async def clear_cache_pattern(pattern: str) -> int:
    """Clear all keys matching pattern"""
    return await cache_manager.clear_pattern(pattern)


# Cache decorator for functions
def cached(ttl_seconds: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix or func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_result = await get_cached(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await set_cached(cache_key, result, ttl_seconds)
            return result
        
        return wrapper
    return decorator