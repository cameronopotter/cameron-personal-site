"""
Analytics and insights Pydantic schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from .base import BaseResponse, DateRangeFilter


class EngagementMetrics(BaseModel):
    """Visitor engagement metrics"""
    total_visitors: int = Field(..., description="Total unique visitors")
    returning_visitors: int = Field(..., description="Returning visitors count")
    average_session_duration: float = Field(..., description="Average session duration in minutes")
    bounce_rate: float = Field(..., ge=0, le=1, description="Bounce rate (0-1)")
    engagement_score: float = Field(..., ge=0, le=1, description="Overall engagement score")
    
    # Interaction metrics
    total_interactions: int = Field(..., description="Total interactions across all visitors")
    interactions_per_session: float = Field(..., description="Average interactions per session")
    seeds_planted: int = Field(..., description="Total seeds planted by visitors")
    
    # Popular content
    most_viewed_projects: List[Dict[str, Any]] = Field(..., description="Most viewed projects with metrics")
    most_engaged_sections: List[Dict[str, Any]] = Field(..., description="Most engaging site sections")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_visitors": 1247,
                "returning_visitors": 289,
                "average_session_duration": 4.7,
                "bounce_rate": 0.23,
                "engagement_score": 0.74,
                "total_interactions": 8934,
                "interactions_per_session": 7.2,
                "seeds_planted": 156,
                "most_viewed_projects": [
                    {
                        "project_id": "123e4567-e89b-12d3-a456-426614174000",
                        "project_name": "Digital Greenhouse",
                        "views": 342,
                        "avg_time_spent": 180,
                        "engagement_rate": 0.85
                    }
                ],
                "most_engaged_sections": [
                    {"section": "project_garden", "engagement_score": 0.89},
                    {"section": "skills_constellation", "engagement_score": 0.76}
                ]
            }
        }
    )


class ProjectAnalytics(BaseModel):
    """Analytics for individual projects"""
    project_id: str = Field(..., description="Project UUID")
    project_name: str = Field(..., description="Project name")
    
    # Growth analytics
    current_stage: str = Field(..., description="Current growth stage")
    total_growth_events: int = Field(..., description="Total growth stage changes")
    growth_velocity: float = Field(..., description="Growth rate over time")
    days_since_last_growth: int = Field(..., description="Days since last growth event")
    
    # Engagement analytics  
    total_views: int = Field(..., description="Total project views")
    unique_visitors: int = Field(..., description="Unique visitors to this project")
    average_view_duration: float = Field(..., description="Average viewing time in seconds")
    interaction_rate: float = Field(..., ge=0, le=1, description="Visitor interaction rate")
    
    # Technical metrics
    commit_frequency: float = Field(..., description="Commits per week")
    code_complexity_trend: str = Field(..., description="Complexity trend over time")
    technology_diversity: int = Field(..., description="Number of technologies used")
    
    # Performance indicators
    demo_click_rate: float = Field(..., description="Rate of demo link clicks")
    github_click_rate: float = Field(..., description="Rate of GitHub link clicks")
    social_shares: int = Field(default=0, description="Social media shares")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "project_name": "Digital Greenhouse", 
                "current_stage": "blooming",
                "total_growth_events": 4,
                "growth_velocity": 1.3,
                "days_since_last_growth": 7,
                "total_views": 342,
                "unique_visitors": 287,
                "average_view_duration": 180.5,
                "interaction_rate": 0.73,
                "commit_frequency": 8.5,
                "code_complexity_trend": "increasing",
                "technology_diversity": 6,
                "demo_click_rate": 0.15,
                "github_click_rate": 0.08,
                "social_shares": 23
            }
        }
    )


class RealtimeMetrics(BaseResponse):
    """Real-time system and engagement metrics"""
    
    # Live activity
    active_visitors: int = Field(..., description="Currently active visitors")
    active_sessions: List[Dict[str, Any]] = Field(..., description="Active session summaries")
    recent_interactions: List[Dict[str, Any]] = Field(..., description="Recent interactions")
    
    # Current garden state
    current_weather: Dict[str, Any] = Field(..., description="Current weather state")
    recent_growth_events: List[Dict[str, Any]] = Field(..., description="Recent project growth")
    system_health: Dict[str, Any] = Field(..., description="System health metrics")
    
    # Performance metrics
    api_response_times: Dict[str, float] = Field(..., description="API endpoint response times")
    database_performance: Dict[str, Any] = Field(..., description="Database performance metrics")
    cache_hit_rates: Dict[str, float] = Field(..., description="Cache performance")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "timestamp": "2024-01-01T12:00:00Z",
                "active_visitors": 8,
                "active_sessions": [
                    {"session_id": "sess_123", "duration": 300, "interactions": 15},
                ],
                "recent_interactions": [
                    {
                        "type": "project_view",
                        "project": "Digital Greenhouse",
                        "timestamp": "2024-01-01T11:58:30Z"
                    }
                ],
                "current_weather": {"type": "aurora", "intensity": 0.7},
                "recent_growth_events": [
                    {
                        "project": "API Project",
                        "from_stage": "growing",
                        "to_stage": "blooming",
                        "timestamp": "2024-01-01T11:45:00Z"
                    }
                ],
                "system_health": {"status": "healthy", "uptime": "99.9%"},
                "api_response_times": {"garden_state": 0.045, "projects": 0.032},
                "database_performance": {"active_connections": 15, "query_time": 0.012},
                "cache_hit_rates": {"redis": 0.94, "application": 0.87}
            }
        }
    )


class AnalyticsDashboard(BaseResponse):
    """Comprehensive analytics dashboard data"""
    
    # Date range for data
    date_range: DateRangeFilter = Field(..., description="Date range for analytics")
    
    # Core metrics
    engagement_metrics: EngagementMetrics = Field(..., description="Visitor engagement data")
    project_analytics: List[ProjectAnalytics] = Field(..., description="Per-project analytics")
    
    # Trends and patterns
    visitor_trends: List[Dict[str, Any]] = Field(..., description="Visitor trends over time")
    growth_trends: List[Dict[str, Any]] = Field(..., description="Project growth trends")
    technology_trends: List[Dict[str, Any]] = Field(..., description="Technology usage trends")
    
    # Performance insights
    top_performing_projects: List[Dict[str, Any]] = Field(..., description="Best performing projects")
    growth_opportunities: List[Dict[str, Any]] = Field(..., description="Growth opportunities identified")
    visitor_behavior_insights: List[str] = Field(..., description="Key visitor behavior insights")
    
    # Comparative data
    period_comparison: Optional[Dict[str, Any]] = Field(None, description="Comparison with previous period")
    seasonal_analysis: Optional[Dict[str, Any]] = Field(None, description="Seasonal pattern analysis")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "timestamp": "2024-01-01T12:00:00Z",
                "date_range": {
                    "start_date": "2023-12-01T00:00:00Z",
                    "end_date": "2024-01-01T00:00:00Z"
                },
                "engagement_metrics": {},
                "project_analytics": [],
                "visitor_trends": [
                    {"date": "2023-12-01", "visitors": 45, "sessions": 67}
                ],
                "growth_trends": [
                    {"date": "2023-12-01", "growth_events": 3, "new_projects": 1}
                ],
                "technology_trends": [
                    {"technology": "React", "usage_growth": 15.5, "projects": 8}
                ],
                "top_performing_projects": [
                    {
                        "project_name": "Digital Greenhouse",
                        "score": 0.92,
                        "metrics": {"views": 342, "engagement": 0.85}
                    }
                ],
                "growth_opportunities": [
                    {
                        "opportunity": "High mobile traffic but low mobile engagement",
                        "potential_impact": "medium",
                        "recommended_action": "Optimize mobile garden interactions"
                    }
                ],
                "visitor_behavior_insights": [
                    "Visitors spend 40% more time on projects with live demos",
                    "Skills constellation is most popular during evening hours"
                ],
                "period_comparison": {
                    "visitor_change": 23.5,
                    "engagement_change": 12.3,
                    "growth_events_change": -5.2
                }
            }
        }
    )


class SystemMetrics(BaseModel):
    """System performance and health metrics"""
    
    # API performance
    total_requests: int = Field(..., description="Total API requests")
    average_response_time: float = Field(..., description="Average response time in seconds")
    error_rate: float = Field(..., ge=0, le=1, description="Error rate (0-1)")
    
    # Database metrics
    database_connections: int = Field(..., description="Active database connections")
    slow_query_count: int = Field(..., description="Number of slow queries")
    database_size_mb: float = Field(..., description="Database size in MB")
    
    # Cache performance  
    cache_hit_rate: float = Field(..., ge=0, le=1, description="Overall cache hit rate")
    redis_memory_usage: float = Field(..., description="Redis memory usage in MB")
    
    # Background tasks
    celery_active_tasks: int = Field(..., description="Active Celery tasks")
    celery_failed_tasks: int = Field(..., description="Failed tasks in last 24h")
    
    # Resource usage
    cpu_usage_percent: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage_percent: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    disk_usage_percent: float = Field(..., ge=0, le=100, description="Disk usage percentage")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_requests": 15678,
                "average_response_time": 0.045,
                "error_rate": 0.002,
                "database_connections": 18,
                "slow_query_count": 3,
                "database_size_mb": 245.7,
                "cache_hit_rate": 0.94,
                "redis_memory_usage": 128.5,
                "celery_active_tasks": 4,
                "celery_failed_tasks": 1,
                "cpu_usage_percent": 23.5,
                "memory_usage_percent": 67.2,
                "disk_usage_percent": 45.8
            }
        }
    )