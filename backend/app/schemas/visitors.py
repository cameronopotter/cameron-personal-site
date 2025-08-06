"""
Visitor session and interaction Pydantic schemas  
"""

from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

from .base import BaseResponse, TimestampMixin, UUIDMixin


class DeviceType(str, Enum):
    """Device types for visitor tracking"""
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"
    UNKNOWN = "unknown"


class InteractionType(str, Enum):
    """Types of visitor interactions"""
    VIEW = "view"
    CLICK = "click"
    HOVER = "hover" 
    SCROLL = "scroll"
    ZOOM = "zoom"
    ROTATE = "rotate"
    DEMO_LAUNCH = "demo_launch"
    GITHUB_VISIT = "github_visit"
    SEED_PLANT = "seed_plant"
    GROWTH_TRIGGER = "growth_trigger"


class VisitorSessionResponse(UUIDMixin, TimestampMixin):
    """Visitor session response with privacy-safe data"""
    session_token: str = Field(..., description="Anonymized session identifier")
    
    # Anonymized visitor info
    country_code: Optional[str] = Field(None, max_length=2, description="Visitor country code")
    device_type: DeviceType = Field(..., description="Device type used")
    browser: Optional[str] = Field(None, description="Browser information")
    screen_resolution: Optional[str] = Field(None, description="Screen resolution")
    
    # Garden interaction data  
    projects_viewed: List[UUID] = Field(default=[], description="Project IDs viewed")
    time_spent_per_project: Dict[str, int] = Field(default={}, description="Time spent per project (seconds)")
    interaction_events: List[Dict[str, Any]] = Field(default=[], description="Interaction events")
    
    # Navigation data
    entry_point: Optional[str] = Field(None, description="Entry point URL")
    journey_path: List[str] = Field(default=[], description="Navigation path through site")
    exit_point: Optional[str] = Field(None, description="Exit point URL")
    
    # Engagement metrics
    total_time_seconds: int = Field(default=0, description="Total session time")
    scroll_depth_percent: Optional[float] = Field(None, ge=0, le=100, description="Maximum scroll depth")
    clicks_count: int = Field(default=0, description="Total clicks")
    seeds_planted: int = Field(default=0, description="Interactive elements engaged")
    
    # Session timing
    started_at: datetime = Field(..., description="Session start time")
    last_activity_at: datetime = Field(..., description="Last activity time")
    ended_at: Optional[datetime] = Field(None, description="Session end time (null if active)")
    
    # Computed metrics
    is_active: bool = Field(..., description="Whether session is still active")
    session_duration_minutes: float = Field(..., description="Session duration in minutes")
    engagement_score: float = Field(..., ge=0, le=1, description="Calculated engagement score (0-1)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "session_token": "anon_sess_abc123def456",
                "country_code": "US",
                "device_type": "desktop",
                "browser": "Chrome 120",
                "screen_resolution": "1920x1080",
                "projects_viewed": ["987fcdeb-51a2-4b3c-d456-426614174000"],
                "time_spent_per_project": {"987fcdeb-51a2-4b3c-d456-426614174000": 180},
                "interaction_events": [
                    {
                        "type": "view",
                        "timestamp": "2024-01-01T10:00:00Z",
                        "data": {"project_id": "987fcdeb-51a2-4b3c-d456-426614174000"}
                    }
                ],
                "entry_point": "https://example.com/",
                "journey_path": ["garden", "project_detail", "skills"],
                "exit_point": "skills",
                "total_time_seconds": 300,
                "scroll_depth_percent": 85.5,
                "clicks_count": 12,
                "seeds_planted": 2,
                "started_at": "2024-01-01T10:00:00Z",
                "last_activity_at": "2024-01-01T10:05:00Z",
                "ended_at": None,
                "is_active": True,
                "session_duration_minutes": 5.0,
                "engagement_score": 0.73,
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-01T10:05:00Z"
            }
        }
    )


class InteractionEvent(BaseModel):
    """Individual visitor interaction event"""
    interaction_type: InteractionType = Field(..., description="Type of interaction")
    duration_seconds: Optional[int] = Field(None, ge=0, description="Duration of interaction")
    metadata: Dict[str, Any] = Field(default={}, description="Additional interaction data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When interaction occurred")
    
    # Optional project context
    project_id: Optional[UUID] = Field(None, description="Project ID if interaction was project-specific")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "interaction_type": "demo_launch",
                "duration_seconds": 45,
                "metadata": {
                    "button_text": "View Live Demo",
                    "page_section": "project_card",
                    "scroll_position": 1200
                },
                "timestamp": "2024-01-01T10:02:30Z",
                "project_id": "987fcdeb-51a2-4b3c-d456-426614174000"
            }
        }
    )


class InteractionResponse(BaseResponse):
    """Response after recording an interaction"""
    interaction_recorded: bool = Field(default=True, description="Whether interaction was recorded")
    session_updated: bool = Field(default=True, description="Whether session was updated")
    engagement_score_delta: Optional[float] = Field(None, description="Change in engagement score")
    
    # Potential side effects
    growth_triggered: bool = Field(default=False, description="Whether interaction triggered project growth")
    analytics_updated: bool = Field(default=False, description="Whether analytics were updated")


class SessionCreateRequest(BaseModel):
    """Request to create a new visitor session"""
    user_agent: Optional[str] = Field(None, description="Browser user agent string")
    screen_resolution: Optional[str] = Field(None, description="Screen resolution")
    entry_point: Optional[str] = Field(None, description="Entry point URL")
    referrer: Optional[str] = Field(None, description="Referrer URL")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "screen_resolution": "1920x1080",
                "entry_point": "https://example.com/",
                "referrer": "https://google.com/search"
            }
        }
    )


class SessionUpdateRequest(BaseModel):
    """Request to update visitor session"""
    projects_viewed: Optional[List[UUID]] = Field(None, description="Add projects to viewed list")
    journey_path: Optional[List[str]] = Field(None, description="Update navigation path")
    scroll_depth_percent: Optional[float] = Field(None, ge=0, le=100, description="Update scroll depth")
    exit_point: Optional[str] = Field(None, description="Set exit point")
    end_session: bool = Field(default=False, description="Mark session as ended")


class VisitorAnalytics(BaseModel):
    """Aggregated visitor analytics"""
    total_sessions: int = Field(..., description="Total number of sessions")
    active_sessions: int = Field(..., description="Currently active sessions")
    average_session_duration: float = Field(..., description="Average session duration in minutes")
    average_engagement_score: float = Field(..., description="Average engagement score")
    
    # Device breakdown
    device_breakdown: Dict[str, int] = Field(..., description="Sessions by device type")
    browser_breakdown: Dict[str, int] = Field(..., description="Sessions by browser")
    country_breakdown: Dict[str, int] = Field(..., description="Sessions by country")
    
    # Engagement metrics
    most_viewed_projects: List[Dict[str, Any]] = Field(..., description="Most popular projects")
    common_journey_paths: List[Dict[str, Any]] = Field(..., description="Common navigation patterns")
    interaction_heatmap: Dict[str, int] = Field(..., description="Interaction frequency by type")
    
    # Time-based patterns
    hourly_activity: List[Dict[str, Any]] = Field(..., description="Activity by hour of day")
    daily_trends: List[Dict[str, Any]] = Field(..., description="Daily visitor trends")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_sessions": 1250,
                "active_sessions": 8,
                "average_session_duration": 4.2,
                "average_engagement_score": 0.65,
                "device_breakdown": {"desktop": 800, "mobile": 350, "tablet": 100},
                "browser_breakdown": {"Chrome": 750, "Safari": 300, "Firefox": 150, "Other": 50},
                "country_breakdown": {"US": 500, "GB": 200, "CA": 150, "Other": 400},
                "most_viewed_projects": [
                    {"project_id": "...", "views": 450, "avg_time": 120},
                ],
                "common_journey_paths": [
                    {"path": ["garden", "project", "skills"], "frequency": 125}
                ],
                "interaction_heatmap": {"view": 2000, "click": 800, "demo_launch": 300},
                "hourly_activity": [{"hour": 14, "sessions": 45}],
                "daily_trends": [{"date": "2024-01-01", "sessions": 67}]
            }
        }
    )