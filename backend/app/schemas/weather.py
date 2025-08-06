"""
Weather-related Pydantic schemas
"""

from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

from .base import BaseResponse, TimestampMixin, UUIDMixin


class WeatherType(str, Enum):
    """Types of weather in the garden"""
    SUNNY = "sunny"
    STORMY = "stormy" 
    CLOUDY = "cloudy"
    AURORA = "aurora"
    STARRY = "starry"
    MISTY = "misty"
    RAINBOW = "rainbow"
    TWILIGHT = "twilight"


class TimeOfDay(str, Enum):
    """Time periods for weather context"""
    DAWN = "dawn"
    DAY = "day"
    DUSK = "dusk" 
    NIGHT = "night"


class Season(str, Enum):
    """Seasons for weather context"""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


class MusicMood(str, Enum):
    """Music mood categories from Spotify"""
    ENERGETIC = "energetic"
    CALM = "calm"
    FOCUSED = "focused"
    CREATIVE = "creative"
    MELANCHOLY = "melancholy"
    UPBEAT = "upbeat"
    AMBIENT = "ambient"


class WeatherStateResponse(UUIDMixin, TimestampMixin):
    """Current or historical weather state response"""
    weather_type: WeatherType = Field(..., description="Type of weather")
    intensity: float = Field(..., ge=0, le=1, description="Weather intensity (0-1)")
    
    # Data sources
    github_commits_today: int = Field(default=0, description="GitHub commits made today")
    coding_hours_today: float = Field(default=0.0, description="Hours spent coding today")
    music_mood: Optional[MusicMood] = Field(None, description="Current music mood")
    actual_weather: Optional[str] = Field(None, description="Real weather conditions")
    
    # Derived indicators
    productivity_score: Optional[float] = Field(None, ge=0, le=1, description="Productivity indicator (0-1)")
    creativity_index: Optional[float] = Field(None, ge=0, le=1, description="Creativity indicator (0-1)")  
    stress_level: Optional[float] = Field(None, ge=0, le=1, description="Stress level indicator (0-1)")
    
    # Temporal context
    time_of_day: TimeOfDay = Field(..., description="Time of day category")
    season: Season = Field(..., description="Current season")
    
    # Duration
    started_at: datetime = Field(..., description="When weather state started")
    ended_at: Optional[datetime] = Field(None, description="When weather state ended (null if current)")
    
    # Computed properties
    is_active: bool = Field(..., description="Whether this weather state is currently active")
    duration_minutes: Optional[float] = Field(None, description="Duration in minutes")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "weather_type": "aurora",
                "intensity": 0.8,
                "github_commits_today": 5,
                "coding_hours_today": 3.5,
                "music_mood": "focused",
                "actual_weather": "clear",
                "productivity_score": 0.7,
                "creativity_index": 0.9,
                "stress_level": 0.3,
                "time_of_day": "night",
                "season": "winter",
                "started_at": "2024-01-01T22:00:00Z",
                "ended_at": None,
                "is_active": True,
                "duration_minutes": 120.5,
                "created_at": "2024-01-01T22:00:00Z",
                "updated_at": "2024-01-01T22:00:00Z"
            }
        }
    )


class MoodUpdateRequest(BaseModel):
    """Request to update weather based on mood indicators"""
    music_mood: Optional[MusicMood] = Field(None, description="Current music mood")
    productivity_indicators: Optional[Dict[str, Any]] = Field(default={}, description="Productivity metrics")
    creativity_signals: Optional[Dict[str, Any]] = Field(default={}, description="Creativity indicators")
    stress_indicators: Optional[Dict[str, Any]] = Field(default={}, description="Stress level data")
    external_weather: Optional[str] = Field(None, description="Real weather conditions")
    force_weather_change: bool = Field(default=False, description="Force immediate weather update")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "music_mood": "energetic",
                "productivity_indicators": {
                    "commits_per_hour": 2.5,
                    "lines_written": 150,
                    "files_modified": 8
                },
                "creativity_signals": {
                    "new_files_created": 3,
                    "experimental_code": True,
                    "readme_updates": 1
                },
                "stress_indicators": {
                    "rapid_commits": False,
                    "late_night_coding": True,
                    "error_rate": 0.1
                },
                "external_weather": "sunny",
                "force_weather_change": False
            }
        }
    )


class WeatherUpdateResponse(BaseResponse):
    """Response after weather update"""
    weather_changed: bool = Field(..., description="Whether weather actually changed")
    previous_weather: Optional[WeatherStateResponse] = Field(None, description="Previous weather state")
    current_weather: WeatherStateResponse = Field(..., description="Current weather state")
    change_reason: Optional[str] = Field(None, description="Reason for weather change")
    next_update_scheduled: Optional[datetime] = Field(None, description="When next automatic update is scheduled")


class WeatherForecast(BaseModel):
    """Weather forecast based on predicted activity"""
    forecast_hours: int = Field(..., ge=1, le=24, description="Hours ahead to forecast")
    predicted_states: List[Dict[str, Any]] = Field(..., description="Predicted weather states")
    confidence: float = Field(..., ge=0, le=1, description="Forecast confidence (0-1)")
    factors_considered: List[str] = Field(..., description="Factors used in prediction")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "forecast_hours": 6,
                "predicted_states": [
                    {
                        "hour_offset": 2,
                        "weather_type": "cloudy", 
                        "intensity": 0.6,
                        "probability": 0.7
                    }
                ],
                "confidence": 0.75,
                "factors_considered": [
                    "historical_coding_patterns",
                    "scheduled_work_sessions",
                    "music_playlist_mood"
                ]
            }
        }
    )


class WeatherInfluenceFactors(BaseModel):
    """Breakdown of factors influencing current weather"""
    github_activity_weight: float = Field(..., description="Influence of GitHub activity")
    music_mood_weight: float = Field(..., description="Influence of music mood")
    time_of_day_weight: float = Field(..., description="Influence of time of day")
    productivity_weight: float = Field(..., description="Influence of productivity metrics")
    external_weather_weight: float = Field(..., description="Influence of real weather")
    historical_pattern_weight: float = Field(..., description="Influence of historical patterns")
    
    total_influence_score: float = Field(..., description="Combined influence score")
    dominant_factor: str = Field(..., description="Most influential factor")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "github_activity_weight": 0.3,
                "music_mood_weight": 0.2,
                "time_of_day_weight": 0.15,
                "productivity_weight": 0.2,
                "external_weather_weight": 0.1,
                "historical_pattern_weight": 0.05,
                "total_influence_score": 0.8,
                "dominant_factor": "github_activity"
            }
        }
    )