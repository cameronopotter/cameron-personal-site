"""
Base classes and utilities for external API integrations.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar('T')


class IntegrationStatus(str, Enum):
    """Integration service status"""
    ACTIVE = "active"
    INACTIVE = "inactive" 
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"


class IntegrationError(Exception):
    """Base exception for integration errors"""
    def __init__(self, message: str, service: str, details: Optional[Dict] = None):
        self.message = message
        self.service = service
        self.details = details or {}
        super().__init__(f"{service}: {message}")


class RateLimitError(IntegrationError):
    """Raised when rate limit is exceeded"""
    def __init__(self, service: str, reset_time: Optional[datetime] = None):
        self.reset_time = reset_time
        message = f"Rate limit exceeded"
        if reset_time:
            message += f", resets at {reset_time}"
        super().__init__(message, service)


class APIResponse(BaseModel, Generic[T]):
    """Standardized API response wrapper"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}
    timestamp: datetime = datetime.utcnow()
    service: str
    
    class Config:
        arbitrary_types_allowed = True


@dataclass
class RateLimitInfo:
    """Rate limiting information"""
    limit: int
    remaining: int
    reset_time: datetime
    retry_after: Optional[int] = None


class BaseIntegration(ABC):
    """Base class for all external API integrations"""
    
    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 1.0
    ):
        self.name = name
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.status = IntegrationStatus.INACTIVE
        self.last_error: Optional[str] = None
        self.rate_limit_info: Optional[RateLimitInfo] = None
        
        # Create HTTP client with proper configuration
        self.client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers=self._get_default_headers()
        )
        
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests"""
        headers = {
            "User-Agent": "DigitalGreenhouse/1.0.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers.update(self._get_auth_headers())
            
        return headers
    
    @abstractmethod
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for this service"""
        pass
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
    
    async def initialize(self) -> bool:
        """Initialize the integration service"""
        try:
            is_healthy = await self.health_check()
            self.status = IntegrationStatus.ACTIVE if is_healthy else IntegrationStatus.ERROR
            logger.info(f"Integration {self.name} initialized with status: {self.status}")
            return is_healthy
        except Exception as e:
            self.last_error = str(e)
            self.status = IntegrationStatus.ERROR
            logger.error(f"Failed to initialize {self.name}: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.client.aclose()
        logger.info(f"Integration {self.name} cleaned up")
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the integration service is healthy"""
        pass
    
    async def make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        retry_count: int = 0
    ) -> httpx.Response:
        """Make an HTTP request with error handling and retries"""
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers
            )
            
            # Update rate limit info from headers
            self._update_rate_limit_info(response.headers)
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = self._get_retry_after(response.headers)
                reset_time = datetime.utcnow() + timedelta(seconds=retry_after)
                self.status = IntegrationStatus.RATE_LIMITED
                raise RateLimitError(self.name, reset_time)
            
            # Handle other HTTP errors
            response.raise_for_status()
            self.status = IntegrationStatus.ACTIVE
            return response
            
        except httpx.HTTPStatusError as e:
            if retry_count < self.max_retries and e.response.status_code >= 500:
                # Retry on server errors
                wait_time = self.backoff_factor * (2 ** retry_count)
                await asyncio.sleep(wait_time)
                return await self.make_request(
                    method, endpoint, params, data, headers, retry_count + 1
                )
            
            self.last_error = f"HTTP {e.response.status_code}: {e.response.text}"
            self.status = IntegrationStatus.ERROR
            raise IntegrationError(self.last_error, self.name)
            
        except Exception as e:
            if retry_count < self.max_retries:
                wait_time = self.backoff_factor * (2 ** retry_count)
                await asyncio.sleep(wait_time)
                return await self.make_request(
                    method, endpoint, params, data, headers, retry_count + 1
                )
            
            self.last_error = str(e)
            self.status = IntegrationStatus.ERROR
            raise IntegrationError(self.last_error, self.name)
    
    def _update_rate_limit_info(self, headers: Dict[str, str]):
        """Update rate limit information from response headers"""
        # Common rate limit header patterns
        limit_headers = ['X-RateLimit-Limit', 'X-Rate-Limit', 'Rate-Limit-Limit']
        remaining_headers = ['X-RateLimit-Remaining', 'X-Rate-Limit-Remaining', 'Rate-Limit-Remaining']
        reset_headers = ['X-RateLimit-Reset', 'X-Rate-Limit-Reset', 'Rate-Limit-Reset']
        
        limit = remaining = reset_timestamp = None
        
        for header in limit_headers:
            if header in headers:
                limit = int(headers[header])
                break
        
        for header in remaining_headers:
            if header in headers:
                remaining = int(headers[header])
                break
        
        for header in reset_headers:
            if header in headers:
                reset_timestamp = int(headers[header])
                break
        
        if all(v is not None for v in [limit, remaining, reset_timestamp]):
            self.rate_limit_info = RateLimitInfo(
                limit=limit,
                remaining=remaining,
                reset_time=datetime.fromtimestamp(reset_timestamp)
            )
    
    def _get_retry_after(self, headers: Dict[str, str]) -> int:
        """Get retry-after time from headers"""
        retry_after = headers.get('Retry-After')
        if retry_after:
            return int(retry_after)
        return 60  # Default to 60 seconds
    
    def is_available(self) -> bool:
        """Check if the integration is currently available"""
        if self.status == IntegrationStatus.RATE_LIMITED:
            if self.rate_limit_info and datetime.utcnow() > self.rate_limit_info.reset_time:
                self.status = IntegrationStatus.ACTIVE
        
        return self.status == IntegrationStatus.ACTIVE
    
    def get_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        return {
            "name": self.name,
            "status": self.status.value,
            "last_error": self.last_error,
            "rate_limit": {
                "limit": self.rate_limit_info.limit if self.rate_limit_info else None,
                "remaining": self.rate_limit_info.remaining if self.rate_limit_info else None,
                "reset_time": self.rate_limit_info.reset_time.isoformat() if self.rate_limit_info else None
            } if self.rate_limit_info else None,
            "api_key_configured": bool(self.api_key)
        }


class WebhookHandler(ABC):
    """Base class for webhook handlers"""
    
    @abstractmethod
    async def handle_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Handle webhook payload"""
        pass
    
    @abstractmethod
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        pass


class DataProcessor(ABC, Generic[T]):
    """Base class for data processors"""
    
    @abstractmethod
    async def process_data(self, raw_data: Dict[str, Any]) -> T:
        """Process raw API data into structured format"""
        pass
    
    @abstractmethod
    def validate_data(self, data: T) -> bool:
        """Validate processed data"""
        pass