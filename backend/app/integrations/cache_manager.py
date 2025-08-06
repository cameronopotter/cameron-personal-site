"""
Multi-layer cache manager for API responses and computed data.
"""

import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
from dataclasses import dataclass
from enum import Enum
import asyncio

from .integration_config import integration_settings

import logging
logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheLayer(str, Enum):
    """Cache layer types"""
    MEMORY = "memory"      # In-memory cache (fastest)
    REDIS = "redis"        # Redis cache (persistent)
    DISK = "disk"          # Disk-based cache (backup)


class CacheStrategy(str, Enum):
    """Cache update strategies"""
    WRITE_THROUGH = "write_through"     # Write to cache and storage simultaneously
    WRITE_BACK = "write_back"           # Write to cache first, storage later
    WRITE_AROUND = "write_around"       # Skip cache, write directly to storage
    REFRESH_AHEAD = "refresh_ahead"     # Proactively refresh before expiry


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    data: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int
    last_accessed: datetime
    size_bytes: int
    tags: List[str]
    serialization: str  # json, pickle, raw


@dataclass
class CacheStats:
    """Cache statistics"""
    total_entries: int
    total_size_bytes: int
    hit_count: int
    miss_count: int
    hit_rate: float
    eviction_count: int
    memory_usage: Dict[str, int]  # By layer
    popular_keys: List[str]
    expired_entries: int


class MemoryCache:
    """In-memory cache implementation"""
    
    def __init__(self, max_size_mb: int = 256):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.entries: Dict[str, CacheEntry] = {}
        self.current_size = 0
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        if key not in self.entries:
            self.stats["misses"] += 1
            return None
        
        entry = self.entries[key]
        
        # Check expiry
        if entry.expires_at and datetime.utcnow() > entry.expires_at:
            await self.delete(key)
            self.stats["misses"] += 1
            return None
        
        # Update access info
        entry.access_count += 1
        entry.last_accessed = datetime.utcnow()
        self.stats["hits"] += 1
        
        return entry.data
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Set value in memory cache"""
        
        # Serialize data and calculate size
        serialized_data, size_bytes = self._serialize_data(value)
        
        # Check if we need to make space
        if key not in self.entries:
            if self.current_size + size_bytes > self.max_size_bytes:
                await self._evict_entries(size_bytes)
        
        # Create entry
        expires_at = None
        if ttl_seconds:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        entry = CacheEntry(
            key=key,
            data=serialized_data,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            access_count=0,
            last_accessed=datetime.utcnow(),
            size_bytes=size_bytes,
            tags=tags or [],
            serialization="raw"
        )
        
        # Remove old entry if exists
        if key in self.entries:
            self.current_size -= self.entries[key].size_bytes
        
        # Add new entry
        self.entries[key] = entry
        self.current_size += size_bytes
        
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete entry from memory cache"""
        if key not in self.entries:
            return False
        
        entry = self.entries[key]
        self.current_size -= entry.size_bytes
        del self.entries[key]
        
        return True
    
    async def clear_by_tag(self, tag: str) -> int:
        """Clear all entries with specific tag"""
        keys_to_delete = [
            key for key, entry in self.entries.items()
            if tag in entry.tags
        ]
        
        for key in keys_to_delete:
            await self.delete(key)
        
        return len(keys_to_delete)
    
    async def _evict_entries(self, needed_bytes: int):
        """Evict entries to make space using LRU strategy"""
        
        # Sort by last accessed time (oldest first)
        sorted_entries = sorted(
            self.entries.items(),
            key=lambda x: x[1].last_accessed
        )
        
        freed_bytes = 0
        keys_to_remove = []
        
        for key, entry in sorted_entries:
            keys_to_remove.append(key)
            freed_bytes += entry.size_bytes
            
            if freed_bytes >= needed_bytes:
                break
        
        # Remove entries
        for key in keys_to_remove:
            await self.delete(key)
            self.stats["evictions"] += 1
    
    def _serialize_data(self, data: Any) -> tuple[Any, int]:
        """Serialize data and calculate size"""
        if isinstance(data, (str, int, float, bool, type(None))):
            # Simple types don't need serialization
            size = len(str(data).encode('utf-8'))
            return data, size
        else:
            # Complex types - just store reference and estimate size
            size = len(str(data).encode('utf-8'))
            return data, size
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory cache statistics"""
        total_hits = self.stats["hits"]
        total_requests = total_hits + self.stats["misses"]
        hit_rate = (total_hits / total_requests) if total_requests > 0 else 0
        
        return {
            "entries": len(self.entries),
            "size_bytes": self.current_size,
            "size_mb": self.current_size / (1024 * 1024),
            "hit_rate": hit_rate,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"]
        }


class RedisCache:
    """Redis cache implementation"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
        self.stats = {"hits": 0, "misses": 0}
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            import aioredis
            self.redis_client = await aioredis.from_url(self.redis_url)
            logger.info("Redis cache initialized")
        except ImportError:
            logger.warning("Redis not available - install aioredis package")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(key)
            if data is None:
                self.stats["misses"] += 1
                return None
            
            self.stats["hits"] += 1
            
            # Deserialize
            if data.startswith(b'json:'):
                return json.loads(data[5:].decode('utf-8'))
            elif data.startswith(b'pickle:'):
                return pickle.loads(data[7:])
            else:
                return data.decode('utf-8')
                
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            self.stats["misses"] += 1
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Set value in Redis"""
        if not self.redis_client:
            return False
        
        try:
            # Serialize data
            if isinstance(value, (dict, list)):
                serialized = b'json:' + json.dumps(value).encode('utf-8')
            elif isinstance(value, (str, int, float, bool)):
                serialized = str(value).encode('utf-8')
            else:
                serialized = b'pickle:' + pickle.dumps(value)
            
            # Set with TTL
            if ttl_seconds:
                await self.redis_client.setex(key, ttl_seconds, serialized)
            else:
                await self.redis_client.set(key, serialized)
            
            # Handle tags (store in separate sets)
            if tags:
                for tag in tags:
                    await self.redis_client.sadd(f"tag:{tag}", key)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False
    
    async def clear_by_tag(self, tag: str) -> int:
        """Clear all keys with specific tag"""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.smembers(f"tag:{tag}")
            if keys:
                count = await self.redis_client.delete(*keys)
                await self.redis_client.delete(f"tag:{tag}")
                return count
            return 0
        except Exception as e:
            logger.error(f"Redis clear_by_tag error for tag {tag}: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        total_hits = self.stats["hits"]
        total_requests = total_hits + self.stats["misses"]
        hit_rate = (total_hits / total_requests) if total_requests > 0 else 0
        
        return {
            "hit_rate": hit_rate,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "connected": self.redis_client is not None
        }


class CacheManager:
    """Multi-layer cache manager"""
    
    def __init__(self):
        self.config = integration_settings.cache
        
        # Initialize cache layers
        self.memory_cache = MemoryCache(max_size_mb=256)
        self.redis_cache = RedisCache(self.config.redis_url)
        
        # Cache configuration
        self.ttl_mapping = self.config.ttl_mapping
        self.default_ttl = self.config.default_ttl_seconds
        
        # Performance tracking
        self.performance_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "write_operations": 0
        }
    
    async def initialize(self):
        """Initialize all cache layers"""
        await self.redis_cache.initialize()
        logger.info("Cache manager initialized")
    
    async def get(
        self, 
        key: str, 
        fetch_function: Optional[Callable[[], Any]] = None,
        ttl_seconds: Optional[int] = None
    ) -> Optional[Any]:
        """Get value from cache with multi-layer fallback"""
        
        self.performance_stats["total_requests"] += 1
        cache_key = self._normalize_key(key)
        
        # Try memory cache first
        value = await self.memory_cache.get(cache_key)
        if value is not None:
            self.performance_stats["cache_hits"] += 1
            return value
        
        # Try Redis cache
        value = await self.redis_cache.get(cache_key)
        if value is not None:
            self.performance_stats["cache_hits"] += 1
            
            # Backfill memory cache
            await self.memory_cache.set(cache_key, value, ttl_seconds)
            return value
        
        # Cache miss - fetch if function provided
        if fetch_function:
            try:
                value = await fetch_function() if asyncio.iscoroutinefunction(fetch_function) else fetch_function()
                if value is not None:
                    await self.set(cache_key, value, ttl_seconds)
                    return value
            except Exception as e:
                logger.error(f"Cache fetch function failed for key {key}: {e}")
        
        self.performance_stats["cache_misses"] += 1
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None,
        layers: Optional[List[CacheLayer]] = None
    ) -> bool:
        """Set value in cache layers"""
        
        self.performance_stats["write_operations"] += 1
        cache_key = self._normalize_key(key)
        
        # Determine TTL
        if ttl_seconds is None:
            ttl_seconds = self._get_ttl_for_key(key)
        
        # Determine which layers to write to
        if layers is None:
            layers = [CacheLayer.MEMORY, CacheLayer.REDIS]
        
        results = []
        
        # Write to memory cache
        if CacheLayer.MEMORY in layers:
            result = await self.memory_cache.set(cache_key, value, ttl_seconds, tags)
            results.append(result)
        
        # Write to Redis cache
        if CacheLayer.REDIS in layers:
            result = await self.redis_cache.set(cache_key, value, ttl_seconds, tags)
            results.append(result)
        
        return any(results)
    
    async def delete(self, key: str, layers: Optional[List[CacheLayer]] = None) -> bool:
        """Delete key from cache layers"""
        
        cache_key = self._normalize_key(key)
        
        if layers is None:
            layers = [CacheLayer.MEMORY, CacheLayer.REDIS]
        
        results = []
        
        if CacheLayer.MEMORY in layers:
            result = await self.memory_cache.delete(cache_key)
            results.append(result)
        
        if CacheLayer.REDIS in layers:
            result = await self.redis_cache.delete(cache_key)
            results.append(result)
        
        return any(results)
    
    async def clear_by_tag(self, tag: str) -> Dict[str, int]:
        """Clear all entries with specific tag from all layers"""
        
        results = {}
        
        memory_cleared = await self.memory_cache.clear_by_tag(tag)
        results["memory"] = memory_cleared
        
        redis_cleared = await self.redis_cache.clear_by_tag(tag)
        results["redis"] = redis_cleared
        
        return results
    
    async def clear_by_pattern(self, pattern: str) -> Dict[str, int]:
        """Clear entries matching a pattern (service-specific)"""
        
        results = {"memory": 0, "redis": 0}
        
        # Clear from memory cache
        keys_to_delete = [
            key for key in self.memory_cache.entries.keys()
            if pattern in key
        ]
        
        for key in keys_to_delete:
            await self.memory_cache.delete(key)
            results["memory"] += 1
        
        # Clear from Redis (would need pattern matching support)
        logger.info(f"Cleared {sum(results.values())} entries matching pattern: {pattern}")
        
        return results
    
    async def invalidate_service_cache(self, service_name: str):
        """Invalidate all cache entries for a specific service"""
        return await self.clear_by_pattern(f"{service_name}:")
    
    def _normalize_key(self, key: str) -> str:
        """Normalize cache key to ensure consistency"""
        return key.lower().replace(" ", "_")
    
    def _get_ttl_for_key(self, key: str) -> int:
        """Get appropriate TTL for a cache key"""
        
        # Check if key matches any specific TTL mapping
        for pattern, ttl in self.ttl_mapping.items():
            if pattern in key:
                return ttl
        
        return self.default_ttl
    
    def _generate_cache_key(
        self, 
        service: str, 
        method: str, 
        params: Dict[str, Any]
    ) -> str:
        """Generate consistent cache key for API calls"""
        
        # Sort parameters for consistent key generation
        sorted_params = sorted(params.items())
        params_string = "&".join(f"{k}={v}" for k, v in sorted_params)
        
        # Hash parameters if too long
        if len(params_string) > 100:
            params_hash = hashlib.md5(params_string.encode()).hexdigest()
            return f"{service}:{method}:{params_hash}"
        
        return f"{service}:{method}:{params_string}"
    
    async def cache_api_call(
        self,
        service: str,
        method: str,
        params: Dict[str, Any],
        fetch_function: Callable,
        ttl_seconds: Optional[int] = None
    ) -> Any:
        """Cache an API call result"""
        
        cache_key = self._generate_cache_key(service, method, params)
        
        return await self.get(
            cache_key,
            fetch_function,
            ttl_seconds
        )
    
    def get_comprehensive_stats(self) -> CacheStats:
        """Get comprehensive cache statistics"""
        
        memory_stats = self.memory_cache.get_stats()
        redis_stats = self.redis_cache.get_stats()
        
        # Calculate overall hit rate
        total_hits = self.performance_stats["cache_hits"]
        total_requests = self.performance_stats["total_requests"]
        overall_hit_rate = (total_hits / total_requests) if total_requests > 0 else 0
        
        return CacheStats(
            total_entries=memory_stats["entries"],
            total_size_bytes=memory_stats["size_bytes"],
            hit_count=total_hits,
            miss_count=self.performance_stats["cache_misses"],
            hit_rate=overall_hit_rate,
            eviction_count=memory_stats["evictions"],
            memory_usage={
                "memory_cache_mb": memory_stats["size_mb"],
                "redis_connected": redis_stats["connected"]
            },
            popular_keys=[],  # Would need tracking
            expired_entries=0  # Would need tracking
        )
    
    async def warm_cache(self, warming_functions: Dict[str, Callable]):
        """Warm cache with commonly accessed data"""
        
        logger.info("Starting cache warming...")
        
        for cache_key, fetch_function in warming_functions.items():
            try:
                value = await fetch_function() if asyncio.iscoroutinefunction(fetch_function) else fetch_function()
                if value is not None:
                    await self.set(cache_key, value)
                    logger.debug(f"Warmed cache for key: {cache_key}")
            except Exception as e:
                logger.warning(f"Failed to warm cache for key {cache_key}: {e}")
        
        logger.info("Cache warming completed")
    
    async def cleanup_expired_entries(self):
        """Cleanup expired entries from memory cache"""
        
        expired_keys = []
        
        for key, entry in self.memory_cache.entries.items():
            if entry.expires_at and datetime.utcnow() > entry.expires_at:
                expired_keys.append(key)
        
        for key in expired_keys:
            await self.memory_cache.delete(key)
        
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)


# Global cache manager instance
cache_manager = CacheManager()