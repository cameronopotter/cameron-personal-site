"""
Digital Greenhouse External API Integrations

This module provides comprehensive external API integrations for the Digital Greenhouse project,
creating a living ecosystem that responds to real-world activities and data.
"""

from .base import BaseIntegration, IntegrationError, RateLimitError
from .github_service import GitHubService
from .spotify_service import SpotifyService  
from .weather_service import WeatherService
from .wakatime_service import WakaTimeService
from .websocket_manager import WebSocketManager
from .growth_engine import GrowthEngine
from .mood_engine import MoodEngine
from .cache_manager import CacheManager
from .rate_limiter import RateLimiter
from .privacy_manager import PrivacyManager

__all__ = [
    "BaseIntegration",
    "IntegrationError", 
    "RateLimitError",
    "GitHubService",
    "SpotifyService",
    "WeatherService", 
    "WakaTimeService",
    "WebSocketManager",
    "GrowthEngine",
    "MoodEngine",
    "CacheManager",
    "RateLimiter",
    "PrivacyManager"
]

__version__ = "1.0.0"