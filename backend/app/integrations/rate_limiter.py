"""
Rate limiting system for API calls and request management.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque

from .integration_config import integration_settings

import logging
logger = logging.getLogger(__name__)


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitResult(str, Enum):
    """Rate limit check results"""
    ALLOWED = "allowed"
    DENIED = "denied"
    WAIT_REQUIRED = "wait_required"


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    service_name: str
    requests_per_minute: int
    burst_limit: int
    strategy: RateLimitStrategy
    window_size_seconds: int = 60
    enabled: bool = True


@dataclass
class RateLimitStatus:
    """Current rate limit status"""
    service_name: str
    requests_made: int
    requests_remaining: int
    reset_time: datetime
    retry_after_seconds: Optional[int]
    current_window: str


@dataclass
class RequestRecord:
    """Individual request record"""
    service_name: str
    timestamp: datetime
    endpoint: str
    success: bool
    response_time_ms: float
    metadata: Dict[str, Any]


class TokenBucket:
    """Token bucket rate limiter implementation"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket"""
        async with self.lock:
            now = time.time()
            
            # Refill tokens based on time elapsed
            time_elapsed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + (time_elapsed * self.refill_rate)
            )
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """Get time to wait before tokens are available"""
        if self.tokens >= tokens:
            return 0.0
        
        needed_tokens = tokens - self.tokens
        return needed_tokens / self.refill_rate


class SlidingWindowLimiter:
    """Sliding window rate limiter implementation"""
    
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = asyncio.Lock()
    
    async def is_allowed(self) -> bool:
        """Check if request is allowed under sliding window"""
        async with self.lock:
            now = time.time()
            cutoff_time = now - self.window_seconds
            
            # Remove old requests outside the window
            while self.requests and self.requests[0] <= cutoff_time:
                self.requests.popleft()
            
            # Check if we're under the limit
            if len(self.requests) < self.limit:
                self.requests.append(now)
                return True
            
            return False
    
    def get_reset_time(self) -> Optional[datetime]:
        """Get when the oldest request will age out"""
        if not self.requests:
            return None
        
        oldest_request = self.requests[0]
        reset_timestamp = oldest_request + self.window_seconds
        return datetime.fromtimestamp(reset_timestamp)


class RateLimiter:
    """Comprehensive rate limiting system"""
    
    def __init__(self):
        self.config = integration_settings.rate_limiting
        
        # Rate limiters by service
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.sliding_windows: Dict[str, SlidingWindowLimiter] = {}
        
        # Request tracking
        self.request_history: List[RequestRecord] = []
        self.service_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_requests": 0,
            "allowed_requests": 0,
            "denied_requests": 0,
            "avg_response_time": 0.0,
            "last_request": None
        })
        
        # Initialize rate limiters for configured services
        self._initialize_rate_limiters()
    
    def _initialize_rate_limiters(self):
        """Initialize rate limiters for all configured services"""
        
        if not self.config.enabled:
            logger.info("Rate limiting disabled")
            return
        
        for service_name, limits in self.config.limits.items():
            # Get authenticated/default limit
            requests_per_minute = limits.get("authenticated", limits.get("default", 60))
            burst_limit = self.config.burst_limits.get(service_name, requests_per_minute // 2)
            
            # Create token bucket (primary limiter)
            refill_rate = requests_per_minute / 60.0  # tokens per second
            self.token_buckets[service_name] = TokenBucket(burst_limit, refill_rate)
            
            # Create sliding window (backup/monitoring)
            self.sliding_windows[service_name] = SlidingWindowLimiter(
                requests_per_minute, 60
            )
            
            logger.info(
                f"Initialized rate limiter for {service_name}: "
                f"{requests_per_minute}/min, burst: {burst_limit}"
            )
    
    async def check_rate_limit(
        self,
        service_name: str,
        endpoint: Optional[str] = None,
        tokens: int = 1
    ) -> Tuple[RateLimitResult, RateLimitStatus]:
        """Check if request is allowed under rate limits"""
        
        if not self.config.enabled:
            return RateLimitResult.ALLOWED, self._get_unlimited_status(service_name)
        
        # Get or create rate limiter for service
        if service_name not in self.token_buckets:
            self._create_default_limiter(service_name)
        
        token_bucket = self.token_buckets[service_name]
        sliding_window = self.sliding_windows[service_name]
        
        # Check token bucket
        can_consume = await token_bucket.consume(tokens)
        
        # Check sliding window
        is_allowed_window = await sliding_window.is_allowed()
        
        # Determine result
        if can_consume and is_allowed_window:
            result = RateLimitResult.ALLOWED
            retry_after = None
        else:
            result = RateLimitResult.DENIED
            wait_time = token_bucket.get_wait_time(tokens)
            retry_after = int(wait_time) if wait_time > 0 else 60
        
        # Get status
        status = await self._get_rate_limit_status(service_name, sliding_window)
        status.retry_after_seconds = retry_after
        
        # Update statistics
        self.service_stats[service_name]["total_requests"] += 1
        if result == RateLimitResult.ALLOWED:
            self.service_stats[service_name]["allowed_requests"] += 1
        else:
            self.service_stats[service_name]["denied_requests"] += 1
        
        return result, status
    
    async def record_request(
        self,
        service_name: str,
        endpoint: str,
        success: bool,
        response_time_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a completed request for monitoring"""
        
        record = RequestRecord(
            service_name=service_name,
            timestamp=datetime.utcnow(),
            endpoint=endpoint,
            success=success,
            response_time_ms=response_time_ms,
            metadata=metadata or {}
        )
        
        self.request_history.append(record)
        
        # Limit history size (keep last 10000 requests)
        if len(self.request_history) > 10000:
            self.request_history = self.request_history[-10000:]
        
        # Update service statistics
        stats = self.service_stats[service_name]
        stats["last_request"] = record.timestamp
        
        # Update average response time (exponential moving average)
        if stats["avg_response_time"] == 0:
            stats["avg_response_time"] = response_time_ms
        else:
            alpha = 0.1  # Smoothing factor
            stats["avg_response_time"] = (
                alpha * response_time_ms + 
                (1 - alpha) * stats["avg_response_time"]
            )
        
        logger.debug(
            f"Recorded request: {service_name}/{endpoint} "
            f"({response_time_ms:.1f}ms, {'success' if success else 'failed'})"
        )
    
    async def wait_for_rate_limit(
        self,
        service_name: str,
        max_wait_seconds: int = 300
    ) -> bool:
        """Wait for rate limit to allow requests"""
        
        if not self.config.enabled:
            return True
        
        if service_name not in self.token_buckets:
            return True
        
        token_bucket = self.token_buckets[service_name]
        wait_time = token_bucket.get_wait_time(1)
        
        if wait_time == 0:
            return True
        
        if wait_time > max_wait_seconds:
            logger.warning(
                f"Rate limit wait time ({wait_time:.1f}s) exceeds maximum ({max_wait_seconds}s)"
            )
            return False
        
        logger.info(f"Waiting {wait_time:.1f}s for rate limit: {service_name}")
        await asyncio.sleep(wait_time)
        return True
    
    def _create_default_limiter(self, service_name: str):
        """Create default rate limiter for unknown service"""
        
        default_requests_per_minute = 60
        default_burst_limit = 30
        
        refill_rate = default_requests_per_minute / 60.0
        self.token_buckets[service_name] = TokenBucket(default_burst_limit, refill_rate)
        self.sliding_windows[service_name] = SlidingWindowLimiter(
            default_requests_per_minute, 60
        )
        
        logger.info(f"Created default rate limiter for {service_name}")
    
    async def _get_rate_limit_status(
        self,
        service_name: str,
        sliding_window: SlidingWindowLimiter
    ) -> RateLimitStatus:
        """Get current rate limit status"""
        
        # Get current window info
        requests_in_window = len(sliding_window.requests)
        limit = sliding_window.limit
        remaining = max(0, limit - requests_in_window)
        
        reset_time = sliding_window.get_reset_time()
        if reset_time is None:
            reset_time = datetime.utcnow() + timedelta(minutes=1)
        
        current_window = f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        
        return RateLimitStatus(
            service_name=service_name,
            requests_made=requests_in_window,
            requests_remaining=remaining,
            reset_time=reset_time,
            retry_after_seconds=None,  # Set by caller
            current_window=current_window
        )
    
    def _get_unlimited_status(self, service_name: str) -> RateLimitStatus:
        """Get status for unlimited/disabled rate limiting"""
        
        return RateLimitStatus(
            service_name=service_name,
            requests_made=0,
            requests_remaining=999999,
            reset_time=datetime.utcnow() + timedelta(hours=1),
            retry_after_seconds=None,
            current_window="unlimited"
        )
    
    def get_service_statistics(self, service_name: str) -> Dict[str, Any]:
        """Get statistics for a specific service"""
        
        stats = self.service_stats[service_name].copy()
        
        # Add recent request analysis
        recent_requests = [
            r for r in self.request_history
            if (r.service_name == service_name and 
                (datetime.utcnow() - r.timestamp).seconds < 3600)
        ]
        
        if recent_requests:
            success_rate = sum(1 for r in recent_requests if r.success) / len(recent_requests)
            avg_response_time = sum(r.response_time_ms for r in recent_requests) / len(recent_requests)
            
            stats.update({
                "recent_requests_1h": len(recent_requests),
                "success_rate_1h": success_rate,
                "avg_response_time_1h": avg_response_time
            })
        
        # Add current rate limit status
        if service_name in self.sliding_windows:
            sliding_window = self.sliding_windows[service_name]
            requests_in_window = len(sliding_window.requests)
            stats.update({
                "current_window_requests": requests_in_window,
                "current_window_limit": sliding_window.limit,
                "current_window_remaining": sliding_window.limit - requests_in_window
            })
        
        return stats
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """Get global rate limiting statistics"""
        
        total_requests = sum(stats["total_requests"] for stats in self.service_stats.values())
        total_allowed = sum(stats["allowed_requests"] for stats in self.service_stats.values())
        total_denied = sum(stats["denied_requests"] for stats in self.service_stats.values())
        
        overall_success_rate = (total_allowed / total_requests) if total_requests > 0 else 0
        
        # Service breakdown
        service_breakdown = {}
        for service_name, stats in self.service_stats.items():
            service_breakdown[service_name] = {
                "requests": stats["total_requests"],
                "success_rate": (stats["allowed_requests"] / stats["total_requests"]) if stats["total_requests"] > 0 else 0,
                "avg_response_time": stats["avg_response_time"]
            }
        
        # Recent activity
        recent_requests = [
            r for r in self.request_history
            if (datetime.utcnow() - r.timestamp).seconds < 3600
        ]
        
        return {
            "enabled": self.config.enabled,
            "total_requests": total_requests,
            "total_allowed": total_allowed,
            "total_denied": total_denied,
            "overall_success_rate": overall_success_rate,
            "services_configured": len(self.token_buckets),
            "recent_requests_1h": len(recent_requests),
            "service_breakdown": service_breakdown
        }
    
    def reset_service_limits(self, service_name: str):
        """Reset rate limits for a specific service"""
        
        if service_name in self.token_buckets:
            # Reset token bucket to full capacity
            token_bucket = self.token_buckets[service_name]
            token_bucket.tokens = float(token_bucket.capacity)
            token_bucket.last_refill = time.time()
        
        if service_name in self.sliding_windows:
            # Clear sliding window
            sliding_window = self.sliding_windows[service_name]
            sliding_window.requests.clear()
        
        logger.info(f"Reset rate limits for service: {service_name}")
    
    def update_service_limits(
        self,
        service_name: str,
        requests_per_minute: int,
        burst_limit: Optional[int] = None
    ):
        """Update rate limits for a service"""
        
        if burst_limit is None:
            burst_limit = requests_per_minute // 2
        
        refill_rate = requests_per_minute / 60.0
        
        # Update token bucket
        self.token_buckets[service_name] = TokenBucket(burst_limit, refill_rate)
        
        # Update sliding window
        self.sliding_windows[service_name] = SlidingWindowLimiter(
            requests_per_minute, 60
        )
        
        logger.info(
            f"Updated rate limits for {service_name}: "
            f"{requests_per_minute}/min, burst: {burst_limit}"
        )
    
    async def cleanup_old_requests(self, hours: int = 24):
        """Clean up old request records"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        old_count = len(self.request_history)
        self.request_history = [
            r for r in self.request_history
            if r.timestamp >= cutoff_time
        ]
        
        removed_count = old_count - len(self.request_history)
        
        logger.info(f"Cleaned up {removed_count} old request records")
        return removed_count


# Global rate limiter instance
rate_limiter = RateLimiter()