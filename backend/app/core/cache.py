"""
Redis caching layer for Digital Greenhouse API
"""

import json
import pickle
from typing import Any, Optional, Union, Dict, List
from datetime import timedelta
import logging

import redis.asyncio as redis
from redis.asyncio import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager with different TTL strategies"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self._connection_pool = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self._connection_pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                decode_responses=False,  # We handle encoding ourselves
                retry_on_timeout=True,
                socket_keepalive=True
            )
            self.redis = Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self.redis.ping()
            logger.info("Redis connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
        if self._connection_pool:
            await self._connection_pool.disconnect()
        logger.info("Redis connection closed")
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for Redis storage"""
        if isinstance(value, (str, int, float)):
            return str(value).encode('utf-8')
        elif isinstance(value, (dict, list)):
            return json.dumps(value, default=str).encode('utf-8')
        else:
            return pickle.dumps(value)
    
    def _deserialize_value(self, value: bytes) -> Any:
        """Deserialize value from Redis"""
        try:
            # Try JSON first (most common)
            return json.loads(value.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                # Try string/numeric
                decoded = value.decode('utf-8')
                # Try to convert to number if possible
                if decoded.isdigit():
                    return int(decoded)
                try:
                    return float(decoded)
                except ValueError:
                    return decoded
            except UnicodeDecodeError:
                # Fall back to pickle
                return pickle.loads(value)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            return self._deserialize_value(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL"""
        if not self.redis:
            return False
        
        try:
            serialized = self._serialize_value(value)
            if ttl_seconds:
                await self.redis.setex(key, ttl_seconds, serialized)
            else:
                await self.redis.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.redis:
            return False
        
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis:
            return False
        
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.redis:
            return 0
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value"""
        if not self.redis:
            return None
        
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """Get time to live for key"""
        if not self.redis:
            return None
        
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return None


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
cache_manager = CacheManager()


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