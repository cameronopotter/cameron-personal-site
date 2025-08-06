# Backend Specification - Digital Greenhouse API
## FastAPI Ecosystem for Interactive Personal Site

---

## 🏗️ Technical Architecture

### Core Stack
```python
# Core Framework
fastapi = "^0.104.1"
uvicorn = "^0.24.0"
pydantic = "^2.5.0"

# Database & ORM
sqlalchemy = "^2.0.23"
alembic = "^1.13.0"
asyncpg = "^0.29.0"
psycopg2-binary = "^2.9.9"

# Caching & Background Tasks  
redis = "^5.0.1"
celery = "^5.3.4"
websockets = "^12.0"

# External Integrations
httpx = "^0.25.2"
requests = "^2.31.0"
python-multipart = "^0.0.6"

# Monitoring & Performance
prometheus-client = "^0.19.0"
structlog = "^23.2.0"
```

### Microservices Architecture
```
🌐 API Gateway (FastAPI)
├── 🌱 Garden Service (Project management)
├── 🌤️ Weather Service (Real-time data aggregation)  
├── 📊 Analytics Service (Visitor tracking & insights)
├── 🔗 Integration Service (External APIs)
└── 🎵 Mood Service (Music & atmosphere)
```

---

## 📊 Database Schema Design

### Core Tables

#### `projects` - The Digital Plants
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    github_repo VARCHAR(255),
    demo_url VARCHAR(500),
    
    -- Garden metaphor fields
    plant_type VARCHAR(50) DEFAULT 'generic', -- tree, flower, vine, etc.
    growth_stage VARCHAR(20) DEFAULT 'seed',  -- seed, sprout, growing, blooming, mature
    planted_date TIMESTAMP DEFAULT NOW(),
    
    -- Visual positioning
    position_x REAL DEFAULT 0,
    position_y REAL DEFAULT 0, 
    position_z REAL DEFAULT 0,
    
    -- Growth factors
    commit_count INTEGER DEFAULT 0,
    lines_of_code INTEGER DEFAULT 0,
    complexity_score REAL DEFAULT 0,
    visitor_interactions INTEGER DEFAULT 0,
    
    -- Metadata
    technologies TEXT[], -- JSONB array of tech stack
    status VARCHAR(20) DEFAULT 'active', -- active, archived, featured
    visibility VARCHAR(20) DEFAULT 'public', -- public, private, unlisted
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_projects_growth_stage ON projects(growth_stage);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_planted_date ON projects(planted_date);
```

#### `project_growth_log` - Growth History Tracking
```sql
CREATE TABLE project_growth_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    
    -- Growth metrics snapshot
    commits_delta INTEGER DEFAULT 0,
    lines_added INTEGER DEFAULT 0,
    lines_removed INTEGER DEFAULT 0,
    complexity_change REAL DEFAULT 0,
    
    -- External activity
    github_activity JSONB, -- commits, PRs, issues
    deployment_events JSONB, -- deployments, releases
    
    -- Visitor engagement
    page_views INTEGER DEFAULT 0,
    interactions INTEGER DEFAULT 0,
    time_spent_minutes INTEGER DEFAULT 0,
    
    -- Growth calculation
    previous_stage VARCHAR(20),
    new_stage VARCHAR(20),
    growth_factor REAL, -- 0-1 scale
    
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_growth_log_project ON project_growth_log(project_id);
CREATE INDEX idx_growth_log_recorded ON project_growth_log(recorded_at);
```

#### `skills` - Skill Constellation System
```sql
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50), -- 'frontend', 'backend', 'devops', 'design'
    
    -- Constellation positioning
    constellation_group VARCHAR(50), -- Which constellation this belongs to
    position_x REAL,
    position_y REAL,
    brightness REAL DEFAULT 0.5, -- 0-1 scale for visual prominence
    
    -- Proficiency tracking
    proficiency_level INTEGER CHECK (proficiency_level >= 1 AND proficiency_level <= 10),
    hours_practiced INTEGER DEFAULT 0,
    projects_used_in INTEGER DEFAULT 0,
    
    -- Learning progression
    first_used_date DATE,
    last_used_date DATE,
    learning_velocity REAL DEFAULT 0, -- How fast skill is improving
    
    -- Metadata
    icon_url VARCHAR(500),
    color_hex VARCHAR(7),
    description TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_constellation ON skills(constellation_group);
```

#### `skill_connections` - How Skills Relate
```sql
CREATE TABLE skill_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_a_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    skill_b_id UUID REFERENCES skills(id) ON DELETE CASCADE,
    
    connection_type VARCHAR(50), -- 'complement', 'prerequisite', 'similar'
    strength REAL DEFAULT 0.5, -- 0-1 scale for connection visibility
    
    -- Evidence of connection
    projects_combined INTEGER DEFAULT 0,
    learning_correlation REAL,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure no duplicate connections
    UNIQUE(skill_a_id, skill_b_id)
);
```

#### `weather_states` - Mood & Atmosphere Tracking
```sql
CREATE TABLE weather_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Weather classification
    weather_type VARCHAR(50), -- 'sunny', 'stormy', 'cloudy', 'aurora', 'starry'
    intensity REAL CHECK (intensity >= 0 AND intensity <= 1),
    
    -- Data sources that influenced this weather
    github_commits_today INTEGER DEFAULT 0,
    coding_hours_today REAL DEFAULT 0,
    music_mood VARCHAR(50), -- from Spotify API
    actual_weather VARCHAR(50), -- real weather influence
    
    -- Emotional/productivity indicators
    productivity_score REAL, -- 0-1 calculated from various metrics
    creativity_index REAL, -- based on project types and commits
    stress_level REAL, -- inferred from coding patterns
    
    -- Timing
    time_of_day VARCHAR(20), -- 'dawn', 'day', 'dusk', 'night'  
    season VARCHAR(20), -- 'spring', 'summer', 'autumn', 'winter'
    
    -- Duration this weather state was active
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_weather_states_started ON weather_states(started_at);
CREATE INDEX idx_weather_states_type ON weather_states(weather_type);
```

#### `visitor_sessions` - Engagement Tracking
```sql
CREATE TABLE visitor_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token VARCHAR(255) UNIQUE,
    
    -- Visitor info (anonymized)
    user_agent TEXT,
    ip_hash VARCHAR(64), -- Hashed IP for privacy
    country_code VARCHAR(2),
    
    -- Garden interaction data
    projects_viewed UUID[], -- Array of project IDs
    time_spent_per_project JSONB, -- {project_id: seconds}
    interaction_events JSONB[], -- Array of interaction objects
    
    -- Navigation pattern
    entry_point VARCHAR(255), -- How they found the site
    journey_path TEXT[], -- Sequence of areas visited
    exit_point VARCHAR(255), -- Last area before leaving
    
    -- Engagement metrics
    total_time_seconds INTEGER DEFAULT 0,
    scroll_depth_percent REAL,
    clicks_count INTEGER DEFAULT 0,
    seeds_planted INTEGER DEFAULT 0, -- Interactive elements engaged
    
    -- Session metadata
    device_type VARCHAR(20), -- 'desktop', 'tablet', 'mobile'
    browser VARCHAR(50),
    screen_resolution VARCHAR(20),
    
    started_at TIMESTAMP DEFAULT NOW(),
    last_activity_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP
);

CREATE INDEX idx_visitor_sessions_started ON visitor_sessions(started_at);
CREATE INDEX idx_visitor_sessions_device ON visitor_sessions(device_type);
```

---

## 🔌 API Endpoint Design

### Garden Management API

#### Project Garden Routes
```python
# GET /api/v1/garden - Get the full garden state
@router.get("/garden")
async def get_garden_state(
    season: Optional[str] = None,
    weather_type: Optional[str] = None,
    visitor_session: str = Depends(get_or_create_session)
) -> GardenState:
    """
    Returns complete garden ecosystem state including:
    - All projects with current growth stages
    - Active weather conditions  
    - Skill constellation positions
    - Personalized content based on visitor history
    """

# POST /api/v1/garden/plant-seed - Plant a new project seed
@router.post("/garden/plant-seed")
async def plant_seed(
    seed_data: SeedPlantingRequest,
    position: Position3D,
    visitor_session: str = Depends(get_visitor_session)
) -> PlantedSeedResponse:
    """
    Creates a new project seed at specified 3D coordinates
    Triggers growth simulation and analytics tracking
    """

# GET /api/v1/garden/weather - Current weather state
@router.get("/garden/weather")
async def get_current_weather() -> WeatherState:
    """Returns current garden weather influenced by:
    - Recent GitHub activity
    - Music listening patterns  
    - Time of day/season
    - Real weather data
    """
```

#### Project Deep Dive Routes  
```python
# GET /api/v1/projects/{project_id} - Detailed project view
@router.get("/projects/{project_id}")
async def get_project_details(
    project_id: UUID,
    visitor_session: str = Depends(get_visitor_session)
) -> ProjectDetailResponse:
    """
    Returns comprehensive project data:
    - Technical details and demo links
    - Growth history and metrics
    - Related projects and skills
    - Interactive content and media
    """

# POST /api/v1/projects/{project_id}/interact - Record interaction
@router.post("/projects/{project_id}/interact")
async def record_project_interaction(
    project_id: UUID,
    interaction: InteractionEvent,
    visitor_session: str = Depends(get_visitor_session)
) -> InteractionResponse:
    """
    Records visitor interaction with project
    Updates growth metrics and analytics
    Returns any triggered growth stage changes
    """
```

### Real-Time Data Integration

#### GitHub Integration Routes
```python
# POST /api/v1/integrations/github/webhook - GitHub webhook handler
@router.post("/integrations/github/webhook")
async def handle_github_webhook(
    webhook_data: GitHubWebhookPayload,
    background_tasks: BackgroundTasks
) -> WebhookResponse:
    """
    Processes GitHub events (commits, PRs, releases)
    Updates project growth metrics
    Triggers weather changes for active coding periods
    """

# GET /api/v1/integrations/github/sync - Manual data sync
@router.get("/integrations/github/sync")
async def sync_github_data(
    background_tasks: BackgroundTasks
) -> SyncResponse:
    """
    Manually trigger GitHub data synchronization
    Updates all project metrics and growth stages
    """
```

#### Music & Mood Integration
```python
# GET /api/v1/integrations/spotify/current - Current listening state
@router.get("/integrations/spotify/current")
async def get_spotify_state() -> SpotifyState:
    """
    Returns current music listening state
    Used to influence garden weather and atmosphere
    """

# POST /api/v1/weather/mood-update - Update based on external mood data
@router.post("/weather/mood-update")
async def update_mood_weather(
    mood_data: MoodUpdateRequest
) -> WeatherUpdateResponse:
    """
    Updates garden weather based on mood indicators:
    - Music genre and energy levels
    - Productivity metrics
    - Time-based patterns
    """
```

### Analytics & Insights

#### Visitor Analytics Routes
```python
# GET /api/v1/analytics/dashboard - Admin dashboard data
@router.get("/analytics/dashboard")
async def get_analytics_dashboard(
    date_range: Optional[str] = "7d"
) -> AnalyticsDashboard:
    """
    Returns comprehensive analytics:
    - Visitor engagement patterns
    - Project interaction heatmaps
    - Growth progression metrics
    - Performance insights
    """

# GET /api/v1/analytics/realtime - Real-time metrics
@router.get("/analytics/realtime")
async def get_realtime_analytics() -> RealtimeMetrics:
    """
    Returns live metrics:
    - Current active visitors
    - Recent interactions
    - Live growth changes
    - System performance
    """
```

---

## 🔄 Background Processing System

### Celery Task Architecture
```python
# Growth calculation tasks
@celery_app.task
def calculate_project_growth(project_id: UUID) -> GrowthResult:
    """
    Periodic task to recalculate project growth stages
    Based on GitHub data, visitor interactions, and time
    """
    
@celery_app.task  
def update_weather_conditions() -> WeatherUpdate:
    """
    Updates garden weather every 15 minutes based on:
    - Recent GitHub activity
    - Music listening patterns
    - Time of day changes
    - Real weather API data
    """

@celery_app.task
def sync_external_data() -> SyncResult:
    """
    Synchronizes data from external APIs:
    - GitHub repositories and commits
    - Spotify listening history  
    - WakaTime coding statistics
    - Weather API updates
    """

@celery_app.task
def generate_skill_insights() -> SkillInsights:
    """
    Analyzes skill usage patterns and generates insights:
    - Skill proficiency progression
    - Skill combination patterns
    - Learning velocity calculations
    - Constellation positioning updates
    """
```

### Caching Strategy
```python
# Redis caching patterns
class CacheConfig:
    # Frequently accessed data
    GARDEN_STATE_TTL = 300  # 5 minutes
    WEATHER_STATE_TTL = 900  # 15 minutes
    PROJECT_DETAILS_TTL = 1800  # 30 minutes
    
    # Analytics data  
    ANALYTICS_DASHBOARD_TTL = 3600  # 1 hour
    REALTIME_METRICS_TTL = 60  # 1 minute
    
    # External API data
    GITHUB_DATA_TTL = 1800  # 30 minutes
    SPOTIFY_DATA_TTL = 300   # 5 minutes

@lru_cache(maxsize=128)
async def get_cached_garden_state(
    season: str, 
    weather: str, 
    visitor_hash: str
) -> GardenState:
    """Cached garden state with visitor personalization"""
```

---

## 🌐 WebSocket Real-Time Updates

### WebSocket Event System
```python
# WebSocket connection manager
class GardenWebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def broadcast_growth_update(self, project_id: UUID, growth_data: GrowthUpdate):
        """Broadcast when a project grows to a new stage"""
        
    async def broadcast_weather_change(self, weather_update: WeatherUpdate):
        """Notify all clients of weather state changes"""
        
    async def send_visitor_interaction(self, interaction: InteractionEvent):
        """Show real-time visitor interactions (anonymized)"""

# WebSocket endpoint
@router.websocket("/ws/garden")
async def garden_websocket_endpoint(websocket: WebSocket):
    """
    Real-time updates for:
    - Project growth changes
    - Weather transitions  
    - Live visitor interactions
    - System announcements
    """
```

### Event Types
```python
class WebSocketEvent(BaseModel):
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]

# Event types:
# - "project_growth" - A project reached a new growth stage
# - "weather_change" - Garden weather updated
# - "visitor_interaction" - Someone interacted with a project
# - "skill_unlock" - New skill added or leveled up
# - "seed_planted" - New project seed planted
# - "system_update" - Admin messages or updates
```

---

## 🔒 Security & Privacy

### Authentication Strategy
```python
# JWT-based admin authentication (for analytics access)
class AdminAuth:
    @staticmethod
    def verify_admin_token(token: str) -> bool:
        """Verify admin access for analytics endpoints"""
        
# Visitor tracking (privacy-focused)
class VisitorTracking:
    @staticmethod
    def hash_visitor_ip(ip: str) -> str:
        """Hash IPs for analytics while preserving privacy"""
        
    @staticmethod
    def anonymize_visitor_data(visitor_data: Dict) -> Dict:
        """Remove PII while keeping useful analytics data"""
```

### Rate Limiting
```python
# Rate limiting configuration
RATE_LIMITS = {
    "garden_state": "100/minute",
    "project_interaction": "30/minute",
    "seed_planting": "5/minute",
    "analytics_dashboard": "10/minute"
}

@limiter.limit("30/minute")
@router.post("/projects/{project_id}/interact")
async def rate_limited_interaction(...):
    """Prevent spam while allowing natural interaction"""
```

---

## 📊 Performance & Monitoring

### Database Performance Optimization
```sql
-- Optimized queries for garden state
CREATE MATERIALIZED VIEW garden_summary AS
SELECT 
    p.id,
    p.name,
    p.growth_stage,
    p.position_x,
    p.position_y,
    p.position_z,
    COUNT(pgl.id) as growth_events,
    AVG(vs.time_spent_seconds) as avg_visit_time
FROM projects p
LEFT JOIN project_growth_log pgl ON p.id = pgl.project_id
LEFT JOIN visitor_sessions vs ON p.id = ANY(vs.projects_viewed)
WHERE p.status = 'active'
GROUP BY p.id, p.name, p.growth_stage, p.position_x, p.position_y, p.position_z;

-- Refresh materialized view every hour
CREATE OR REPLACE FUNCTION refresh_garden_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW garden_summary;
END;
$$ LANGUAGE plpgsql;
```

### Metrics Collection
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# API metrics
api_requests_total = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
request_duration = Histogram('request_duration_seconds', 'Request duration')
active_websockets = Gauge('active_websockets_total', 'Active WebSocket connections')

# Business metrics  
project_interactions = Counter('project_interactions_total', 'Project interactions', ['project_id'])
growth_stage_changes = Counter('growth_stage_changes_total', 'Growth stage changes', ['from_stage', 'to_stage'])
weather_changes = Counter('weather_changes_total', 'Weather changes', ['weather_type'])
```

---

## 🚀 Deployment & Scaling

### Container Configuration
```dockerfile
# Multi-stage build for FastAPI
FROM python:3.11-slim as base

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./app /app
WORKDIR /app

# Production setup
FROM base as production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Environment Configuration
```python
# Pydantic settings management
class Settings(BaseSettings):
    # Database
    database_url: str
    redis_url: str
    
    # External APIs
    github_token: str
    spotify_client_id: str
    spotify_client_secret: str
    weather_api_key: str
    
    # Security
    secret_key: str
    admin_password: str
    
    # Performance
    max_connections: int = 100
    cache_ttl: int = 300
    
    class Config:
        env_file = ".env"
```

This backend specification creates a robust, scalable API that powers the interactive garden ecosystem while maintaining excellent performance and user privacy standards.