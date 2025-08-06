"""
Configuration settings for external API integrations.
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field
from pydantic import BaseSettings, Field

from ..core.config import settings


@dataclass
class GitHubConfig:
    """GitHub integration configuration"""
    token: str = field(default="")
    username: str = field(default="")
    base_url: str = field(default="https://api.github.com")
    webhook_secret: str = field(default="")
    repositories: List[str] = field(default_factory=list)
    rate_limit_per_hour: int = field(default=5000)
    webhook_events: List[str] = field(default_factory=lambda: ["push", "pull_request", "issues", "release"])
    
    @property
    def is_configured(self) -> bool:
        return bool(self.token and self.username)


@dataclass  
class SpotifyConfig:
    """Spotify integration configuration"""
    client_id: str = field(default="")
    client_secret: str = field(default="")
    redirect_uri: str = field(default="http://localhost:8000/auth/spotify/callback")
    scope: str = field(default="user-read-currently-playing user-read-playback-state user-top-read")
    base_url: str = field(default="https://api.spotify.com/v1")
    refresh_token: str = field(default="")
    
    @property
    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)


@dataclass
class WeatherConfig:
    """Weather API configuration"""
    api_key: str = field(default="")
    base_url: str = field(default="https://api.openweathermap.org/data/2.5")
    default_location: str = field(default="London,UK")
    units: str = field(default="metric")  # metric, imperial, kelvin
    update_interval_minutes: int = field(default=15)
    include_forecast: bool = field(default=True)
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


@dataclass
class WakaTimeConfig:
    """WakaTime integration configuration"""
    api_key: str = field(default="")
    base_url: str = field(default="https://wakatime.com/api/v1")
    username: str = field(default="")
    sync_interval_hours: int = field(default=4)
    include_projects: List[str] = field(default_factory=list)
    exclude_projects: List[str] = field(default_factory=list)
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


@dataclass
class SocialConfig:
    """Social media integration configuration"""
    twitter_bearer_token: str = field(default="")
    linkedin_access_token: str = field(default="")
    rss_feeds: List[str] = field(default_factory=list)
    update_interval_hours: int = field(default=6)
    max_posts_per_sync: int = field(default=50)
    
    @property
    def is_configured(self) -> bool:
        return bool(self.twitter_bearer_token or self.linkedin_access_token or self.rss_feeds)


@dataclass
class CacheConfig:
    """Caching configuration"""
    redis_url: str = field(default="redis://localhost:6379/0")
    default_ttl_seconds: int = field(default=300)  # 5 minutes
    max_memory: str = field(default="256mb")
    
    # Different TTL for different data types
    ttl_mapping: Dict[str, int] = field(default_factory=lambda: {
        "github_repos": 1800,      # 30 minutes
        "github_commits": 300,     # 5 minutes
        "spotify_current": 30,     # 30 seconds
        "spotify_features": 3600,  # 1 hour
        "weather_current": 900,    # 15 minutes
        "weather_forecast": 3600,  # 1 hour
        "wakatime_stats": 3600,    # 1 hour
        "growth_analysis": 1800,   # 30 minutes
        "mood_analysis": 300,      # 5 minutes
        "visitor_analytics": 86400 # 24 hours
    })


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    enabled: bool = field(default=True)
    
    # Service-specific rate limits (requests per minute)
    limits: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        "github": {
            "authenticated": 83,    # 5000/hour = ~83/minute
            "unauthenticated": 10   # 60/hour = 1/minute  
        },
        "spotify": {
            "default": 100          # No official limit, but be conservative
        },
        "weather": {
            "default": 10           # 1000/day = ~0.7/minute, buffer included
        },
        "wakatime": {
            "default": 10           # Conservative estimate
        }
    })
    
    # Burst allowances
    burst_limits: Dict[str, int] = field(default_factory=lambda: {
        "github": 20,
        "spotify": 30,
        "weather": 5,
        "wakatime": 5
    })


@dataclass
class WebSocketConfig:
    """WebSocket configuration"""
    enabled: bool = field(default=True)
    max_connections: int = field(default=1000)
    ping_interval: int = field(default=30)
    ping_timeout: int = field(default=10)
    max_message_size: int = field(default=1024 * 1024)  # 1MB
    
    # Event filtering
    event_filters: Dict[str, List[str]] = field(default_factory=lambda: {
        "default": ["commit_pushed", "music_changed", "weather_updated", "growth_stage_changed"],
        "admin": ["*"]  # Admin gets all events
    })
    
    # Message queuing
    max_queue_size: int = field(default=100)
    queue_timeout_seconds: int = field(default=30)


@dataclass
class PrivacyConfig:
    """Privacy and data protection configuration"""
    anonymize_visitor_data: bool = field(default=True)
    data_retention_days: int = field(default=30)
    gdpr_compliance: bool = field(default=True)
    
    # PII anonymization
    hash_ip_addresses: bool = field(default=True)
    hash_user_agents: bool = field(default=True)
    
    # Data export/deletion
    enable_data_export: bool = field(default=True)
    enable_data_deletion: bool = field(default=True)
    
    # Consent management
    require_consent: bool = field(default=False)
    consent_categories: List[str] = field(default_factory=lambda: [
        "essential", "analytics", "integrations", "marketing"
    ])


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    prometheus_enabled: bool = field(default=True)
    prometheus_port: int = field(default=8001)
    
    # Health check intervals
    health_check_interval_seconds: int = field(default=30)
    integration_timeout_seconds: int = field(default=10)
    
    # Alerting thresholds
    error_rate_threshold: float = field(default=0.1)  # 10%
    response_time_threshold_ms: float = field(default=1000)  # 1 second
    availability_threshold: float = field(default=0.95)  # 95%
    
    # Log levels per service
    log_levels: Dict[str, str] = field(default_factory=lambda: {
        "github": "INFO",
        "spotify": "INFO", 
        "weather": "INFO",
        "wakatime": "INFO",
        "websockets": "INFO",
        "cache": "INFO",
        "rate_limiter": "WARNING"
    })


class IntegrationSettings(BaseSettings):
    """Main integration settings class"""
    
    # Service configurations
    github: GitHubConfig = field(default_factory=GitHubConfig)
    spotify: SpotifyConfig = field(default_factory=SpotifyConfig)
    weather: WeatherConfig = field(default_factory=WeatherConfig)
    wakatime: WakaTimeConfig = field(default_factory=WakaTimeConfig)
    social: SocialConfig = field(default_factory=SocialConfig)
    
    # Infrastructure configurations
    cache: CacheConfig = field(default_factory=CacheConfig)
    rate_limiting: RateLimitConfig = field(default_factory=RateLimitConfig)
    websockets: WebSocketConfig = field(default_factory=WebSocketConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Feature flags
    enable_github: bool = field(default=True)
    enable_spotify: bool = field(default=False)
    enable_weather: bool = field(default=True)
    enable_wakatime: bool = field(default=False)
    enable_social: bool = field(default=False)
    enable_real_time_events: bool = field(default=True)
    enable_mood_synthesis: bool = field(default=True)
    enable_growth_prediction: bool = field(default=True)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_nested_delimiter = "_"
    
    def __post_init__(self):
        """Initialize configurations from environment variables"""
        # Load from main settings
        self.github.token = getattr(settings, 'github_token', '') or ''
        self.github.username = getattr(settings, 'github_username', '') or ''
        
        self.spotify.client_id = getattr(settings, 'spotify_client_id', '') or ''
        self.spotify.client_secret = getattr(settings, 'spotify_client_secret', '') or ''
        self.spotify.redirect_uri = getattr(settings, 'spotify_redirect_uri', self.spotify.redirect_uri)
        
        self.weather.api_key = getattr(settings, 'weather_api_key', '') or ''
        self.weather.base_url = getattr(settings, 'weather_api_base_url', self.weather.base_url)
        
        self.wakatime.api_key = getattr(settings, 'wakatime_api_key', '') or ''
        
        self.cache.redis_url = getattr(settings, 'redis_url', self.cache.redis_url)
        
        # Sync feature flags with main settings
        self.enable_github = getattr(settings, 'enable_github_integration', True)
        self.enable_spotify = getattr(settings, 'enable_spotify_integration', False)
        self.enable_weather = getattr(settings, 'enable_weather_integration', True)
    
    def get_enabled_services(self) -> List[str]:
        """Get list of enabled integration services"""
        enabled = []
        
        if self.enable_github and self.github.is_configured:
            enabled.append("github")
        
        if self.enable_spotify and self.spotify.is_configured:
            enabled.append("spotify")
        
        if self.enable_weather and self.weather.is_configured:
            enabled.append("weather")
        
        if self.enable_wakatime and self.wakatime.is_configured:
            enabled.append("wakatime")
        
        if self.enable_social and self.social.is_configured:
            enabled.append("social")
        
        return enabled
    
    def validate_configurations(self) -> Dict[str, List[str]]:
        """Validate all configurations and return errors"""
        errors = {}
        
        if self.enable_github and not self.github.is_configured:
            errors["github"] = ["Missing GitHub token or username"]
        
        if self.enable_spotify and not self.spotify.is_configured:
            errors["spotify"] = ["Missing Spotify client ID or secret"]
        
        if self.enable_weather and not self.weather.is_configured:
            errors["weather"] = ["Missing weather API key"]
        
        if self.enable_wakatime and not self.wakatime.is_configured:
            errors["wakatime"] = ["Missing WakaTime API key"]
        
        return errors


# Global integration settings instance
def get_integration_settings() -> IntegrationSettings:
    """Get integration settings with proper initialization"""
    settings_instance = IntegrationSettings()
    settings_instance.__post_init__()
    return settings_instance


integration_settings = get_integration_settings()