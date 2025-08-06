"""
Pydantic schemas for external API responses and data models.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator


# GitHub API Schemas
class GitHubRepository(BaseModel):
    """GitHub repository data"""
    id: int
    name: str
    full_name: str
    description: Optional[str] = None
    private: bool
    html_url: str
    clone_url: str
    git_url: str
    ssh_url: str
    language: Optional[str] = None
    languages_url: str
    size: int
    stargazers_count: int
    watchers_count: int
    forks_count: int
    open_issues_count: int
    default_branch: str
    created_at: datetime
    updated_at: datetime
    pushed_at: Optional[datetime] = None
    topics: List[str] = []
    license: Optional[Dict[str, Any]] = None
    
    # Additional computed fields
    complexity_score: Optional[float] = None
    growth_stage: Optional[str] = None
    last_analysis: Optional[datetime] = None


class GitHubCommit(BaseModel):
    """GitHub commit data"""
    sha: str
    message: str
    author_name: str
    author_email: str
    author_date: datetime
    committer_name: str
    committer_email: str
    committer_date: datetime
    url: str
    additions: Optional[int] = None
    deletions: Optional[int] = None
    changed_files: Optional[int] = None
    
    # Additional fields for analysis
    repository: str
    impact_score: Optional[float] = None
    commit_type: Optional[str] = None  # feature, fix, refactor, etc.


class GitHubLanguageStats(BaseModel):
    """GitHub repository language statistics"""
    repository: str
    languages: Dict[str, int]  # language -> bytes of code
    total_bytes: int
    primary_language: Optional[str] = None
    diversity_score: Optional[float] = None
    
    @validator('primary_language', pre=True, always=True)
    def set_primary_language(cls, v, values):
        if not v and 'languages' in values:
            languages = values['languages']
            if languages:
                return max(languages, key=languages.get)
        return v


class GitHubActivity(BaseModel):
    """GitHub user activity summary"""
    username: str
    total_commits: int
    total_repositories: int
    total_stars_received: int
    total_forks_received: int
    languages: Dict[str, int]
    recent_activity_score: float
    growth_velocity: float
    last_commit_date: Optional[datetime] = None
    
    # Extended activity metrics
    commits_today: int = 0
    commits_this_week: int = 0
    commits_this_month: int = 0
    active_repositories: List[str] = []
    lines_added: int = 0
    lines_deleted: int = 0
    consistency_score: float = 0.0


class GitHubWebhookEvent(BaseModel):
    """GitHub webhook event data"""
    event_type: str  # push, pull_request, issues, etc.
    action: Optional[str] = None
    repository: GitHubRepository
    sender: Dict[str, Any]
    commits: Optional[List[Dict[str, Any]]] = None
    pull_request: Optional[Dict[str, Any]] = None
    issue: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Spotify API Schemas
class SpotifyAudioFeatures(BaseModel):
    """Spotify audio features"""
    track_id: str
    danceability: float = Field(ge=0.0, le=1.0)
    energy: float = Field(ge=0.0, le=1.0)
    speechiness: float = Field(ge=0.0, le=1.0)
    acousticness: float = Field(ge=0.0, le=1.0)
    instrumentalness: float = Field(ge=0.0, le=1.0)
    liveness: float = Field(ge=0.0, le=1.0)
    valence: float = Field(ge=0.0, le=1.0)  # musical positiveness
    tempo: float = Field(gt=0.0)
    time_signature: int = Field(ge=3, le=7)
    duration_ms: int = Field(gt=0)
    loudness: float
    mode: int = Field(ge=0, le=1)  # 0 = minor, 1 = major
    key: int = Field(ge=0, le=11)


class SpotifyTrack(BaseModel):
    """Spotify track data"""
    id: str
    name: str
    artists: List[str]
    album: str
    duration_ms: int
    popularity: int = Field(ge=0, le=100)
    explicit: bool
    external_urls: Dict[str, str]
    preview_url: Optional[str] = None
    audio_features: Optional[SpotifyAudioFeatures] = None


class SpotifyCurrentlyPlaying(BaseModel):
    """Currently playing track on Spotify"""
    is_playing: bool
    track: Optional[SpotifyTrack] = None
    progress_ms: Optional[int] = None
    timestamp: datetime
    context_type: Optional[str] = None  # album, artist, playlist
    shuffle_state: Optional[bool] = None
    repeat_state: Optional[str] = None  # off, context, track


class SpotifyMoodAnalysis(BaseModel):
    """Mood analysis from Spotify data"""
    energy_level: float = Field(ge=0.0, le=1.0)
    positivity: float = Field(ge=0.0, le=1.0)  # valence
    intensity: float = Field(ge=0.0, le=1.0)
    mood_category: str  # energetic, calm, happy, melancholic, etc.
    tempo_category: str  # slow, moderate, fast
    listening_context: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0)


# Weather API Schemas
class WeatherCondition(BaseModel):
    """Weather condition data"""
    id: int
    main: str  # Rain, Snow, Clear, etc.
    description: str
    icon: str


class WeatherData(BaseModel):
    """Current weather data"""
    location: str
    country: str
    temperature: float  # Celsius
    feels_like: float
    humidity: int = Field(ge=0, le=100)
    pressure: int
    visibility: Optional[int] = None  # meters
    uv_index: Optional[float] = None
    wind_speed: float  # m/s
    wind_direction: Optional[int] = None  # degrees
    cloud_cover: int = Field(ge=0, le=100)
    conditions: List[WeatherCondition]
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None
    timestamp: datetime


class WeatherForecast(BaseModel):
    """Weather forecast data"""
    location: str
    forecasts: List[WeatherData]
    forecast_type: str  # hourly, daily
    valid_until: datetime


# WakaTime API Schemas
class WakaTimeProject(BaseModel):
    """WakaTime project data"""
    name: str
    total_seconds: int
    percent: float
    digital: str  # formatted time string
    text: str
    hours: int
    minutes: int


class WakaTimeLanguage(BaseModel):
    """WakaTime language data"""
    name: str
    total_seconds: int
    percent: float
    digital: str
    text: str
    hours: int
    minutes: int


class WakaTimeStats(BaseModel):
    """WakaTime coding statistics"""
    user_id: str
    username: str
    total_seconds: int
    daily_average: int
    languages: List[WakaTimeLanguage]
    projects: List[WakaTimeProject]
    operating_systems: List[Dict[str, Any]]
    editors: List[Dict[str, Any]]
    date_range: Dict[str, str]
    is_up_to_date: bool


class WakaTimeActivity(BaseModel):
    """WakaTime activity summary"""
    username: str
    total_coding_time: int  # seconds
    productivity_score: float = Field(ge=0.0, le=1.0)
    focus_score: float = Field(ge=0.0, le=1.0)
    primary_language: Optional[str] = None
    active_projects: List[str]
    coding_velocity: float
    last_activity: Optional[datetime] = None


# Garden Growth Schemas
class GrowthStage(str, Enum):
    """Plant growth stages"""
    SEED = "seed"
    SPROUT = "sprout"
    SEEDLING = "seedling"
    YOUNG = "young"
    MATURE = "mature"
    FLOWERING = "flowering"
    FRUITING = "fruiting"


class ProjectGrowthData(BaseModel):
    """Project growth analysis data"""
    project_id: str
    project_name: str
    current_stage: GrowthStage
    growth_progress: float = Field(ge=0.0, le=1.0)
    health_score: float = Field(ge=0.0, le=1.0)
    
    # Growth factors
    commit_frequency: float
    code_complexity: float
    project_age_days: int
    contributor_count: int
    issue_resolution_rate: float
    
    # Metrics
    total_commits: int
    lines_of_code: int
    recent_activity_score: float
    community_engagement: float
    
    # Predictions
    predicted_next_stage: Optional[GrowthStage] = None
    growth_velocity: float
    estimated_days_to_next_stage: Optional[int] = None
    
    last_updated: datetime


class GardenMoodState(BaseModel):
    """Garden atmospheric mood state"""
    overall_mood: str  # calm, energetic, focused, creative, etc.
    energy_level: float = Field(ge=0.0, le=1.0)
    creativity_index: float = Field(ge=0.0, le=1.0)
    productivity_level: float = Field(ge=0.0, le=1.0)
    
    # Contributing factors
    music_influence: float = Field(ge=0.0, le=1.0)
    weather_influence: float = Field(ge=0.0, le=1.0)
    coding_activity_influence: float = Field(ge=0.0, le=1.0)
    time_of_day_influence: float = Field(ge=0.0, le=1.0)
    
    # Atmospheric properties
    lighting_intensity: float = Field(ge=0.0, le=1.0)
    color_temperature: float = Field(ge=2000.0, le=8000.0)  # Kelvin
    particle_density: float = Field(ge=0.0, le=1.0)
    wind_intensity: float = Field(ge=0.0, le=1.0)
    
    # Metadata
    confidence_score: float = Field(ge=0.0, le=1.0)
    last_updated: datetime
    contributing_data_sources: List[str]


# Real-time Event Schemas
class EventType(str, Enum):
    """Types of real-time events"""
    COMMIT_PUSHED = "commit_pushed"
    MUSIC_CHANGED = "music_changed"
    WEATHER_UPDATED = "weather_updated"
    GROWTH_STAGE_CHANGED = "growth_stage_changed"
    MOOD_SHIFTED = "mood_shifted"
    VISITOR_JOINED = "visitor_joined"
    PROJECT_ACTIVITY = "project_activity"
    SYSTEM_ALERT = "system_alert"


class RealTimeEvent(BaseModel):
    """Real-time event data"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    source_service: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    priority: int = Field(ge=1, le=10, default=5)
    expires_at: Optional[datetime] = None


class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str
    event: Optional[RealTimeEvent] = None
    data: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    client_id: Optional[str] = None


# Analytics Schemas
class VisitorAnalytics(BaseModel):
    """Anonymous visitor analytics"""
    session_id: str
    session_duration: int  # seconds
    page_views: int
    interactions: int
    device_type: str  # mobile, tablet, desktop
    browser_family: str
    os_family: str
    country: Optional[str] = None
    referrer: Optional[str] = None
    engagement_score: float = Field(ge=0.0, le=1.0)
    timestamp: datetime


class SystemMetrics(BaseModel):
    """System performance metrics"""
    cpu_usage: float = Field(ge=0.0, le=100.0)
    memory_usage: float = Field(ge=0.0, le=100.0)
    active_connections: int
    api_response_time: float  # milliseconds
    database_pool_usage: float = Field(ge=0.0, le=1.0)
    cache_hit_rate: float = Field(ge=0.0, le=1.0)
    error_rate: float = Field(ge=0.0, le=1.0)
    timestamp: datetime


class IntegrationHealthStatus(BaseModel):
    """Integration service health status"""
    service_name: str
    status: str  # active, inactive, error, rate_limited
    last_successful_request: Optional[datetime] = None
    error_count: int = 0
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    uptime_percentage: float = Field(ge=0.0, le=100.0)
    last_health_check: datetime


# Social Media Schemas
class SocialMediaPost(BaseModel):
    """Social media post data"""
    id: str
    platform: str  # twitter, linkedin, rss
    content: str
    author: str
    created_at: datetime
    url: Optional[str] = None
    likes: int = 0
    shares: int = 0
    comments: int = 0
    hashtags: List[str] = []
    mentions: List[str] = []
    engagement_rate: float = Field(ge=0.0, le=1.0)
    tech_relevance_score: float = Field(ge=0.0, le=1.0)


class TechTrendAnalysis(BaseModel):
    """Technology trend analysis from social media"""
    trending_topics: List[Dict[str, Any]]
    programming_languages: Dict[str, int]
    tech_tools: Dict[str, int]
    sentiment_scores: Dict[str, float]  # positive, negative, neutral
    innovation_signals: List[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
    analysis_period_days: int
    posts_analyzed: int


# Growth Engine Schemas  
class GrowthMetrics(BaseModel):
    """Comprehensive project growth metrics"""
    project_name: str
    current_stage: str  # seed, seedling, sapling, young_tree, mature_tree, ancient_tree
    growth_score: float = Field(ge=0.0, le=1.0)
    velocity: float  # Growth units per day
    momentum: float  # Rate of acceleration
    
    # Individual factor scores
    commit_score: float = Field(ge=0.0, le=1.0)
    complexity_score: float = Field(ge=0.0, le=1.0)
    time_score: float = Field(ge=0.0, le=1.0)
    engagement_score: float = Field(ge=0.0, le=1.0)
    age_score: float = Field(ge=0.0, le=1.0)
    consistency_score: float = Field(ge=0.0, le=1.0)
    innovation_score: float = Field(ge=0.0, le=1.0)
    
    # Predictions
    next_stage_eta: Optional[int] = None  # Days to next stage
    projected_growth: float = Field(ge=0.0, le=1.0)  # Expected growth in 30 days
    
    # Metadata
    last_updated: datetime
    confidence: float = Field(ge=0.0, le=1.0)


class PortfolioOverview(BaseModel):
    """Portfolio growth overview"""
    total_projects: int
    avg_growth_score: float = Field(ge=0.0, le=1.0)
    stage_distribution: Dict[str, int]
    most_active_project: Optional[Dict[str, Any]] = None
    projects: List[Dict[str, Any]]


# Mood Engine Schemas
class MoodSynthesis(BaseModel):
    """Synthesized garden mood"""
    primary_atmosphere: str
    weather_pattern: str
    
    # Mood components (0.0 to 1.0)
    energy_level: float = Field(ge=0.0, le=1.0)
    focus_level: float = Field(ge=0.0, le=1.0)
    creativity_level: float = Field(ge=0.0, le=1.0)
    serenity_level: float = Field(ge=0.0, le=1.0)
    intensity_level: float = Field(ge=0.0, le=1.0)
    
    # Visual properties
    color_palette: List[str]
    lighting_style: str
    particle_density: float = Field(ge=0.0, le=1.0)
    wind_strength: float = Field(ge=0.0, le=1.0)
    
    # Audio properties
    ambient_sounds: List[str]
    music_influence: float = Field(ge=0.0, le=1.0)
    
    # Growth modifiers
    growth_rate_modifier: float = Field(ge=0.5, le=2.0)
    bloom_probability: float = Field(ge=0.0, le=1.0)
    
    # Metadata
    confidence: float = Field(ge=0.0, le=1.0)
    data_sources: List[str]
    last_updated: datetime
    transitions: Dict[str, float]


class MoodTrends(BaseModel):
    """Mood analysis trends over time"""
    period_hours: int
    moods_analyzed: int
    averages: Dict[str, float]
    most_common: Dict[str, str]
    trends: Dict[str, str]
    data_source_usage: Dict[str, float]


# Cache Manager Schemas
class CacheStats(BaseModel):
    """Cache performance statistics"""
    total_entries: int
    total_size_bytes: int
    hit_count: int
    miss_count: int
    hit_rate: float = Field(ge=0.0, le=1.0)
    eviction_count: int
    memory_usage: Dict[str, Any]
    expired_entries: int


# Rate Limiter Schemas
class RateLimitStatus(BaseModel):
    """Rate limit status for a service"""
    service_name: str
    requests_made: int
    requests_remaining: int
    reset_time: datetime
    retry_after_seconds: Optional[int] = None
    current_window: str


class RateLimitStats(BaseModel):
    """Global rate limiting statistics"""
    enabled: bool
    total_requests: int
    total_allowed: int
    total_denied: int
    overall_success_rate: float = Field(ge=0.0, le=1.0)
    services_configured: int
    recent_requests_1h: int
    service_breakdown: Dict[str, Dict[str, Any]]


# Privacy Manager Schemas
class ConsentRecord(BaseModel):
    """User consent record"""
    consent_id: str
    visitor_id: str
    categories: Dict[str, bool]
    granted_at: datetime
    expires_at: Optional[datetime] = None
    consent_string: str


class DataSubjectRequest(BaseModel):
    """GDPR data subject request"""
    request_id: str
    request_type: str  # access, rectification, erasure, portability
    visitor_id: str
    contact_email: Optional[str] = None
    requested_at: datetime
    processed_at: Optional[datetime] = None
    status: str  # pending, processing, completed, rejected
    

class PrivacyDashboard(BaseModel):
    """Privacy compliance dashboard data"""
    consent_summary: Dict[str, Any]
    data_subject_requests: Dict[str, Any]
    retention_policies: Dict[str, Dict[str, Any]]
    recent_activity: Dict[str, Any]
    compliance_features: Dict[str, bool]


# Task Scheduler Schemas
class TaskExecution(BaseModel):
    """Task execution record"""
    execution_id: str
    task_id: str
    status: str  # pending, running, completed, failed, retrying, cancelled
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    context: Dict[str, Any] = {}


class SchedulerStats(BaseModel):
    """Task scheduler statistics"""
    is_running: bool
    registered_tasks: int
    scheduled_tasks: int
    running_tasks: int
    recent_executions: int
    total_executions: int
    stats: Dict[str, Any]


# Analytics Schemas
class VisitorProfile(BaseModel):
    """Anonymous visitor profile"""
    visitor_id: str
    first_visit: datetime
    last_visit: datetime
    total_visits: int
    total_session_time: int
    avg_session_time: float
    engagement_level: str
    favorite_projects: List[str]
    preferred_times: List[int]
    device_info: Dict[str, Any]
    interaction_patterns: Dict[str, int]
    journey_segments: List[str]
    conversion_events: List[str]


class SessionAnalysis(BaseModel):
    """Visitor session analysis"""
    session_id: str
    visitor_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: int
    page_views: int
    interactions: int
    bounce_rate: float = Field(ge=0.0, le=1.0)
    engagement_score: float = Field(ge=0.0, le=1.0)
    journey_path: List[str]
    conversion_achieved: bool
    device_type: str
    exit_point: str


class EngagementMetrics(BaseModel):
    """Comprehensive engagement metrics"""
    total_visitors: int
    unique_visitors_24h: int
    avg_session_duration: float
    bounce_rate: float = Field(ge=0.0, le=1.0)
    pages_per_session: float
    conversion_rate: float = Field(ge=0.0, le=1.0)
    engagement_distribution: Dict[str, int]
    popular_content: List[Dict[str, Any]]
    traffic_sources: Dict[str, int]
    device_breakdown: Dict[str, int]
    geographic_distribution: Dict[str, int]
    peak_hours: List[int]
    retention_metrics: Dict[str, float]


# WebSocket Schemas
class WebSocketConnectionInfo(BaseModel):
    """WebSocket connection information"""
    connection_id: str
    role: str  # visitor, admin, system
    connected_at: datetime
    last_ping: Optional[datetime] = None
    subscribed_events: List[str]
    metadata: Dict[str, Any] = {}
    is_active: bool = True


class WebSocketStats(BaseModel):
    """WebSocket connection statistics"""
    total_connections: int
    connections_by_role: Dict[str, int]
    max_connections: int
    recent_events_count: int
    uptime_seconds: int


# Integration Status Schemas
class ServiceStatus(BaseModel):
    """Individual service status"""
    name: str
    status: str  # active, inactive, error, rate_limited, maintenance
    last_error: Optional[str] = None
    rate_limit: Optional[Dict[str, Any]] = None
    api_key_configured: bool


class IntegrationOverview(BaseModel):
    """Overall integration status"""
    enabled_services: List[str]
    service_health: Dict[str, ServiceStatus]
    cache_stats: CacheStats
    rate_limit_stats: RateLimitStats
    websocket_stats: WebSocketStats
    scheduler_stats: SchedulerStats
    privacy_stats: PrivacyDashboard
    last_updated: datetime