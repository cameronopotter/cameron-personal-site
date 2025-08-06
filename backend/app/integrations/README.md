# Digital Greenhouse Integration System

A comprehensive external API integration and real-time data pipeline system that transforms your digital activities into a living, breathing garden ecosystem.

## 🌟 Overview

The Digital Greenhouse Integration System connects multiple external services to create a magical experience where:

- **GitHub commits** make plants grow and evolve through different stages
- **Music from Spotify** influences the garden's atmospheric mood and weather patterns
- **Real weather data** affects the garden's environment and growth conditions
- **Coding time from WakaTime** accelerates plant development and productivity
- **Social media activity** adds dynamic elements and trend analysis
- **Visitor analytics** provide insights while maintaining privacy compliance

## 🏗️ System Architecture

### External API Services
- **GitHub Service** - Repository data, commits, activity tracking, webhook events
- **Spotify Service** - Currently playing music, audio features, mood analysis
- **Weather Service** - Current weather, forecasts, seasonal influences
- **WakaTime Service** - Coding time, productivity metrics, project analysis
- **Social Service** - Twitter, LinkedIn, RSS feeds, tech trend analysis

### Data Processing Engines
- **Growth Engine** - Project growth calculation, stage progression, predictive modeling
- **Mood Engine** - Multi-source mood synthesis, atmospheric generation
- **Analytics Processor** - Visitor journey analysis, engagement metrics, privacy-compliant tracking

### Infrastructure Components
- **WebSocket Manager** - Real-time event broadcasting, connection management
- **Cache Manager** - Multi-layer caching (memory + Redis), performance optimization
- **Task Scheduler** - Background job orchestration, automated data synchronization
- **Rate Limiter** - API rate limiting, request management, service protection
- **Privacy Manager** - GDPR compliance, data anonymization, user rights management

## 🚀 Quick Start

### 1. Environment Setup

Copy the environment template:
```bash
cp .env.example .env
```

Configure your API keys and settings in `.env`:

```env
# Required for basic functionality
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username
WEATHER_API_KEY=your_openweathermap_api_key

# Optional integrations
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
WAKATIME_API_KEY=your_wakatime_api_key

# Infrastructure
REDIS_URL=redis://localhost:6379/0
ENABLE_RATE_LIMITING=true
```

### 2. Initialize Services

```python
from app.integrations import (
    cache_manager, task_scheduler, websocket_manager,
    GitHubService, WeatherService, GrowthEngine, MoodEngine
)

# Initialize infrastructure
await cache_manager.initialize()
await task_scheduler.start()

# Schedule default tasks
task_scheduler.schedule_default_tasks()

# Initialize services
github_service = GitHubService()
weather_service = WeatherService()
growth_engine = GrowthEngine()
mood_engine = MoodEngine()
```

### 3. Run Integration Tests

```bash
python -m app.integrations.integration_test
```

## 📋 API Services Documentation

### GitHub Integration

**Purpose**: Track repository activity, commits, and project growth.

```python
github_service = GitHubService()

# Get user repositories
repos = await github_service.get_user_repositories()

# Get repository commits
commits = await github_service.get_repository_commits("my-project", limit=50)

# Get activity summary
activity = await github_service.get_user_activity_summary(days=30)

# Calculate growth metrics
growth = await github_service.calculate_growth_metrics("my-project")
```

**Webhook Support**: Real-time events for push, pull requests, issues, releases.

### Weather Integration

**Purpose**: Provide environmental context and atmospheric mood influence.

```python
weather_service = WeatherService()

# Get current weather
current = await weather_service.get_current_weather()

# Get weather forecast
forecast = await weather_service.get_weather_forecast(days=5)

# Analyze atmospheric mood
mood = weather_service.analyze_atmospheric_mood(current.data)

# Get comprehensive data
data = await weather_service.get_comprehensive_weather_data()
```

### Spotify Integration

**Purpose**: Music-based mood analysis and atmospheric influence.

```python
spotify_service = SpotifyService()

# Get currently playing track
current = await spotify_service.get_currently_playing()

# Analyze current mood from music
mood = await spotify_service.analyze_current_mood()

# Get listening trends
trends = await spotify_service.get_listening_trends(days=7)
```

## 🔄 Data Processing Engines

### Growth Engine

Calculates project growth stages based on multiple factors:

```python
growth_engine = GrowthEngine()

# Calculate project growth
metrics = await growth_engine.calculate_project_growth("my-project")

# Get portfolio overview
portfolio = await growth_engine.get_portfolio_overview()
```

**Growth Stages**: seed → seedling → sapling → young_tree → mature_tree → ancient_tree

**Growth Factors**:
- Commit frequency and consistency
- Code complexity and language diversity
- Time invested (from WakaTime)
- External engagement (stars, forks)
- Project age and maturity
- Innovation indicators

### Mood Engine

Synthesizes atmospheric conditions from multiple data sources:

```python
mood_engine = MoodEngine()

# Synthesize current mood
mood = await mood_engine.synthesize_current_mood()

# Get mood trends
trends = await mood_engine.get_mood_trends(hours=24)
```

**Mood Components**:
- Energy level (0.0-1.0)
- Focus level (0.0-1.0)
- Creativity level (0.0-1.0)
- Serenity level (0.0-1.0)
- Intensity level (0.0-1.0)

**Influences**:
- Music (40% weight) - Audio features, current track mood
- Weather (30% weight) - Current conditions, seasonal factors
- Productivity (20% weight) - Coding activity, focus patterns
- Time of day (10% weight) - Circadian rhythm context

## 🔧 Infrastructure Components

### Cache Manager

Multi-layer caching for optimal performance:

```python
from app.integrations.cache_manager import cache_manager

# Initialize cache
await cache_manager.initialize()

# Cache data
await cache_manager.set("github:repos", repos_data, ttl_seconds=1800)

# Get cached data with fallback
data = await cache_manager.get("github:repos", fetch_function=lambda: fetch_repos())

# Cache API calls
result = await cache_manager.cache_api_call(
    service="github",
    method="get_repos", 
    params={},
    fetch_function=github_api_call
)
```

**Cache Layers**:
- Memory cache (fastest, limited size)
- Redis cache (persistent, shared)
- Automatic fallback and backfill

### Task Scheduler

Background job orchestration with dependencies:

```python
from app.integrations.task_scheduler import task_scheduler

# Start scheduler
await task_scheduler.start()

# Execute task immediately
execution_id = await task_scheduler.execute_task_now("github_sync")

# Schedule custom task
task_scheduler.register_task(TaskDefinition(
    task_id="custom_task",
    function=my_task_function,
    priority=TaskPriority.HIGH
))

# Schedule with interval
task_scheduler.schedule_task("custom_task", interval_seconds=3600)
```

**Built-in Tasks**:
- GitHub data sync (every 30 minutes)
- Weather data sync (every 15 minutes) 
- Mood synthesis (every 3 minutes)
- Growth calculation (every hour)
- Cache maintenance (daily)
- Health checks (every 5 minutes)

### WebSocket Manager

Real-time event broadcasting:

```python
from app.integrations.websocket_manager import websocket_manager, WebSocketEvent

# Broadcast event
await websocket_manager.broadcast_event(WebSocketEvent(
    type=EventType.COMMIT_PUSHED,
    data={"repository": "my-project", "commits": 3},
    timestamp=datetime.utcnow(),
    source="github_sync"
))

# Get connection stats
stats = websocket_manager.get_connection_stats()
```

**Event Types**:
- `commit_pushed` - New commits detected
- `music_changed` - Currently playing music changed
- `weather_updated` - Weather conditions updated
- `growth_stage_changed` - Project reached new growth stage
- `atmosphere_changed` - Garden mood/atmosphere shifted
- `visitor_joined/left` - Visitor tracking events

### Rate Limiter

API rate limiting and request management:

```python
from app.integrations.rate_limiter import rate_limiter

# Check rate limit
result, status = await rate_limiter.check_rate_limit("github", tokens=1)

if result == RateLimitResult.ALLOWED:
    # Make API call
    response = await make_github_request()
    
    # Record request metrics
    await rate_limiter.record_request(
        service_name="github",
        endpoint="/repos",
        success=True,
        response_time_ms=250.0
    )
```

**Features**:
- Token bucket algorithm
- Service-specific limits
- Automatic retry handling
- Request metrics tracking
- Burst allowances

### Privacy Manager

GDPR compliance and data protection:

```python
from app.integrations.privacy_manager import privacy_manager

# Generate anonymous visitor ID
visitor_id = privacy_manager.generate_visitor_id(ip_address, user_agent)

# Record consent
consent_id = privacy_manager.record_consent(
    visitor_id=visitor_id,
    categories={
        ConsentCategory.ESSENTIAL: True,
        ConsentCategory.ANALYTICS: True
    },
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent")
)

# Process data subject request
request_id = privacy_manager.create_data_subject_request(
    request_type="access",
    visitor_id=visitor_id
)
```

**Privacy Features**:
- IP address hashing
- User agent anonymization
- Data retention policies
- GDPR subject rights (access, deletion, portability)
- Consent management
- Privacy audit logging

## 📊 Real-time Events

### Event Flow

1. **External API Change** (GitHub commit, music change, weather update)
2. **Service Detection** (webhook, polling, real-time sync)
3. **Data Processing** (growth calculation, mood synthesis)
4. **Event Broadcasting** (WebSocket to connected clients)
5. **Garden Updates** (plant growth, atmosphere changes, visual effects)

### Event Examples

```json
{
  "type": "commit_pushed",
  "data": {
    "repository": "digital-greenhouse",
    "commit_count": 3,
    "author": "developer",
    "impact_score": 0.8
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "github_sync"
}

{
  "type": "atmosphere_changed", 
  "data": {
    "old_atmosphere": "serene_morning",
    "new_atmosphere": "creative_evening",
    "energy_change": 0.4,
    "data_sources": ["spotify", "weather", "time"]
  },
  "timestamp": "2024-01-15T10:31:00Z",
  "source": "mood_engine"
}
```

## 🎯 Configuration

### Service Configuration

Each service can be configured via environment variables:

```python
from app.integrations.integration_config import integration_settings

# Check service availability
if integration_settings.github.is_configured:
    github_service = GitHubService()

# Get enabled services
enabled_services = integration_settings.get_enabled_services()

# Validate configuration
errors = integration_settings.validate_configurations()
```

### Feature Flags

Enable/disable features dynamically:

```env
ENABLE_GITHUB_INTEGRATION=true
ENABLE_SPOTIFY_INTEGRATION=false
ENABLE_REAL_TIME_EVENTS=true
ENABLE_MOOD_SYNTHESIS=true
ENABLE_GROWTH_PREDICTION=true
```

### Rate Limit Configuration

Customize rate limits per service:

```env
GITHUB_RATE_LIMIT=80
SPOTIFY_RATE_LIMIT=100
WEATHER_RATE_LIMIT=10
```

## 🔒 Security & Privacy

### API Key Security
- Environment variable storage
- No hardcoded credentials
- Encrypted storage options
- Token refresh handling

### Privacy Protection
- Automatic data anonymization
- IP address hashing
- User agent sanitization
- Configurable data retention
- GDPR compliance tools

### Rate Limiting
- Service protection
- Abuse prevention
- Fair usage enforcement
- Automatic backoff

## 📈 Monitoring & Observability

### Health Monitoring
```python
# Service health checks
health_status = await github_service.health_check()

# Integration overview
from app.integrations import get_integration_status
status = await get_integration_status()
```

### Performance Metrics
- API response times
- Cache hit rates
- Error rates
- Request volumes
- Service availability

### Logging
Structured logging with configurable levels:
```env
LOG_LEVEL_GITHUB=INFO
LOG_LEVEL_SPOTIFY=DEBUG
LOG_LEVEL_RATE_LIMITER=WARNING
```

## 🧪 Testing

### Integration Tests

Run comprehensive test suite:
```bash
python -m app.integrations.integration_test
```

Test specific services:
```python
from app.integrations.integration_test import IntegrationTester

tester = IntegrationTester()
await tester._test_github_service()
```

### Mock Data

Enable mock data for development:
```env
ENABLE_MOCK_DATA=true
```

## 🚀 Deployment

### Docker Configuration

The integration system is containerized and works with the existing Docker setup:

```dockerfile
# Additional environment variables in docker-compose.yml
environment:
  - GITHUB_TOKEN=${GITHUB_TOKEN}
  - WEATHER_API_KEY=${WEATHER_API_KEY}
  - REDIS_URL=redis://redis:6379/0
```

### Production Checklist

- [ ] Configure all required API keys
- [ ] Set up Redis for caching
- [ ] Configure rate limiting
- [ ] Enable privacy features
- [ ] Set appropriate log levels
- [ ] Configure monitoring
- [ ] Test webhook endpoints
- [ ] Verify CORS settings

## 🔧 Troubleshooting

### Common Issues

**GitHub API Rate Limiting**
```bash
# Check rate limit status
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
```

**Weather API Key Issues**
```bash
# Test weather API
curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY"
```

**Redis Connection Issues**
```python
# Test Redis connection
import redis
r = redis.from_url("redis://localhost:6379/0")
r.ping()  # Should return True
```

### Debug Mode

Enable debug logging:
```env
DEBUG_MODE=true
LOG_LEVEL_GITHUB=DEBUG
LOG_LEVEL_CACHE=DEBUG
```

### Health Checks

Monitor service health:
```python
from app.integrations.task_scheduler import task_scheduler

# Run health check task
await task_scheduler.execute_task_now("health_checks")

# Get scheduler status
stats = task_scheduler.get_scheduler_stats()
```

## 🤝 Contributing

### Adding New Integrations

1. Create service class extending `BaseIntegration`
2. Implement required methods (`health_check`, `_get_auth_headers`)
3. Add configuration to `integration_config.py`
4. Create tests in `integration_test.py`
5. Update environment template

### Integration Template

```python
from .base import BaseIntegration, APIResponse

class NewService(BaseIntegration):
    def __init__(self):
        super().__init__(
            name="new_service",
            base_url="https://api.example.com",
            api_key=config.api_key
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}
    
    async def health_check(self) -> bool:
        try:
            response = await self.make_request("GET", "/health")
            return response.status_code == 200
        except Exception:
            return False
    
    async def get_data(self) -> APIResponse[Any]:
        # Implementation here
        pass
```

## 📚 API Reference

### Core Classes

- `BaseIntegration` - Base class for all API services
- `APIResponse[T]` - Standardized API response wrapper
- `WebSocketEvent` - Real-time event data structure
- `TaskDefinition` - Background task configuration
- `CacheEntry` - Cache item with metadata

### Configuration Classes

- `IntegrationSettings` - Main configuration
- `GitHubConfig`, `SpotifyConfig`, etc. - Service-specific config
- `CacheConfig`, `RateLimitConfig` - Infrastructure config

### Data Models

- `GitHubRepository`, `GitHubCommit` - GitHub data
- `SpotifyTrack`, `AudioFeatures` - Spotify data  
- `WeatherData`, `WeatherForecast` - Weather data
- `GrowthMetrics`, `MoodSynthesis` - Processed data

## 📄 License

This integration system is part of the Digital Greenhouse project and follows the same license terms.

---

*The Digital Greenhouse Integration System - Where code becomes life, and data becomes magic.* 🌱✨