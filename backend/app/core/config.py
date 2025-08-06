"""
Core configuration settings for Digital Greenhouse API
"""

import os
from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Main application settings"""
    
    # Application metadata
    app_name: str = "Digital Greenhouse API"
    app_version: str = "1.0.0"
    app_description: str = "FastAPI backend for an interactive 3D personal portfolio site"
    debug: bool = False
    
    # Security
    secret_key: str = Field(..., min_length=32, description="Secret key for JWT tokens")
    access_token_expire_minutes: int = 30
    admin_password: str = Field(..., min_length=8, description="Admin dashboard password")
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/digital_greenhouse"
    async_database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/digital_greenhouse"
    
    # Redis/Caching
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300
    
    # External API keys
    github_token: Optional[str] = Field(None, description="GitHub personal access token")
    github_username: str = Field("", description="GitHub username for repo data")
    
    spotify_client_id: Optional[str] = Field(None, description="Spotify client ID")
    spotify_client_secret: Optional[str] = Field(None, description="Spotify client secret")
    spotify_redirect_uri: str = "http://localhost:8000/auth/spotify/callback"
    
    weather_api_key: Optional[str] = Field(None, description="Weather API key")
    weather_api_base_url: str = "https://api.openweathermap.org/data/2.5"
    
    wakatime_api_key: Optional[str] = Field(None, description="WakaTime API key")
    
    # CORS settings
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:3001", "https://localhost:3000"]
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    allowed_headers: List[str] = ["*"]
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_minutes: int = 1
    
    # Background tasks
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # Monitoring and logging
    log_level: str = "INFO"
    enable_prometheus: bool = True
    sentry_dsn: Optional[str] = None
    
    # Garden simulation settings
    growth_calculation_interval_minutes: int = 15
    weather_update_interval_minutes: int = 15
    data_sync_interval_hours: int = 4
    
    # File storage
    upload_max_size_mb: int = 10
    allowed_file_extensions: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"]
    
    # Performance
    max_concurrent_requests: int = 100
    database_pool_size: int = 20
    database_max_overflow: int = 30
    
    # Feature flags
    enable_websockets: bool = True
    enable_analytics: bool = True
    enable_visitor_tracking: bool = True
    enable_github_integration: bool = True
    enable_spotify_integration: bool = False
    enable_weather_integration: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @validator('allowed_origins', pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator('allowed_file_extensions', pre=True)  
    def parse_file_extensions(cls, v):
        """Parse file extensions from string or list"""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    @property
    def database_config(self) -> Dict[str, Any]:
        """Database configuration dictionary"""
        return {
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "pool_pre_ping": True,
            "pool_recycle": 300
        }
    
    @property
    def redis_config(self) -> Dict[str, Any]:
        """Redis configuration dictionary"""
        return {
            "url": self.redis_url,
            "decode_responses": True,
            "retry_on_timeout": True,
            "socket_keepalive": True,
            "socket_keepalive_options": {}
        }
    
    @property
    def celery_config(self) -> Dict[str, Any]:
        """Celery configuration dictionary"""
        return {
            "broker_url": self.celery_broker_url,
            "result_backend": self.celery_result_backend,
            "task_serializer": "json",
            "accept_content": ["json"],
            "result_serializer": "json",
            "timezone": "UTC",
            "enable_utc": True,
            "beat_schedule": {
                "calculate-growth": {
                    "task": "app.tasks.calculate_project_growth",
                    "schedule": self.growth_calculation_interval_minutes * 60,
                },
                "update-weather": {
                    "task": "app.tasks.update_weather_conditions", 
                    "schedule": self.weather_update_interval_minutes * 60,
                },
                "sync-external-data": {
                    "task": "app.tasks.sync_external_data",
                    "schedule": self.data_sync_interval_hours * 3600,
                }
            }
        }


class TestSettings(Settings):
    """Settings for testing environment"""
    
    database_url: str = "postgresql://postgres:password@localhost:5432/digital_greenhouse_test"
    async_database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/digital_greenhouse_test"
    redis_url: str = "redis://localhost:6379/15"  # Use different Redis DB for tests
    
    # Disable external integrations in tests
    enable_github_integration: bool = False
    enable_spotify_integration: bool = False
    enable_weather_integration: bool = False
    
    # Shorter intervals for testing
    growth_calculation_interval_minutes: int = 1
    weather_update_interval_minutes: int = 1
    data_sync_interval_hours: int = 1
    
    # Test-specific settings
    debug: bool = True
    log_level: str = "DEBUG"


# Environment-based settings selection
def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "test":
        return TestSettings()
    else:
        return Settings()


# Global settings instance
settings = get_settings()