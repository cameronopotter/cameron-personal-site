# Digital Greenhouse Backend API

A comprehensive FastAPI backend powering an interactive 3D personal portfolio site with real-time growth simulation, weather systems, and visitor analytics.

## 🌱 Features

- **Garden State Management**: Dynamic 3D positioning and growth stages for projects
- **Real-time Growth Simulation**: Projects evolve based on GitHub activity and visitor engagement
- **Weather System**: Mood-based atmospheric conditions influenced by coding activity and music
- **Skills Constellation**: Interactive skill visualization with connection mapping
- **Visitor Analytics**: Privacy-focused engagement tracking and behavioral analysis
- **WebSocket Updates**: Real-time garden state synchronization
- **Background Tasks**: Automated growth calculations and data synchronization
- **Caching Layer**: Redis-powered performance optimization
- **External Integrations**: GitHub, Spotify, Weather APIs

## 🏗️ Architecture

- **FastAPI**: Async Python web framework
- **PostgreSQL**: Primary database with UUID support
- **Redis**: Caching and message broker
- **Celery**: Background task processing
- **SQLAlchemy 2.0**: Modern async ORM
- **Alembic**: Database migrations
- **Docker**: Containerized deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development

1. **Clone and setup**:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database setup**:
   ```bash
   # Create database
   createdb digital_greenhouse
   
   # Run migrations
   alembic upgrade head
   ```

4. **Start services**:
   ```bash
   # Terminal 1: API Server
   python scripts/run_dev.py
   
   # Terminal 2: Celery Worker
   python scripts/run_celery.py worker
   
   # Terminal 3: Celery Beat (optional)
   python scripts/run_celery.py beat
   ```

### Docker Development

```bash
# Start all services
docker-compose up

# API will be available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

## 📊 API Endpoints

### Garden Management
- `GET /api/v1/garden/` - Complete garden state
- `POST /api/v1/garden/plant-seed` - Plant new project seed
- `GET /api/v1/garden/weather` - Current weather conditions
- `GET /api/v1/garden/health` - Garden ecosystem health

### Project Management  
- `GET /api/v1/projects/` - List projects with pagination
- `POST /api/v1/projects/` - Create new project
- `GET /api/v1/projects/{id}` - Project details with analytics
- `POST /api/v1/projects/{id}/interact` - Record visitor interaction

### Analytics
- `GET /api/v1/analytics/dashboard` - Comprehensive analytics
- `GET /api/v1/analytics/realtime` - Live metrics
- `GET /api/v1/visitors/analytics` - Visitor behavior insights

### Real-time Updates
- `WebSocket /ws/garden` - Live garden state updates

## 🔧 Configuration

Key environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/digital_greenhouse
REDIS_URL=redis://localhost:6379/0

# External APIs (optional)
GITHUB_TOKEN=your-github-token
SPOTIFY_CLIENT_ID=your-spotify-client-id
WEATHER_API_KEY=your-weather-api-key

# Features
ENABLE_GITHUB_INTEGRATION=true
ENABLE_WEBSOCKETS=true
ENABLE_ANALYTICS=true
```

See `.env.example` for complete configuration options.

## 🎯 Background Tasks

The system runs several automated background tasks:

- **Growth Calculation**: Updates project growth stages every 15 minutes
- **Weather Updates**: Refreshes garden weather based on activity
- **Data Synchronization**: Fetches latest data from external APIs
- **Analytics Processing**: Aggregates visitor behavior patterns
- **Maintenance**: Cleans up old sessions and optimizes database

## 🔐 Security & Privacy

- **Visitor Privacy**: IP addresses are hashed, no PII stored
- **Rate Limiting**: Configurable per-endpoint limits
- **CORS Protection**: Configurable origin whitelist  
- **Input Validation**: Comprehensive Pydantic schemas
- **Error Handling**: Sanitized error responses in production

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app

# Integration tests
pytest tests/integration/
```

## 📈 Monitoring

- **Health Checks**: `/health` endpoint with component status
- **Metrics**: Basic metrics at `/metrics`
- **Logging**: Structured logging with configurable levels
- **Error Tracking**: Optional Sentry integration

## 🚀 Deployment

### Production Docker

```bash
# Build production image
docker build --target production -t digital-greenhouse-api .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up
```

### Environment Setup

1. Configure production environment variables
2. Set up SSL certificates 
3. Configure reverse proxy (nginx)
4. Set up monitoring and logging
5. Configure backup strategies

## 🤝 Development

### Code Quality

```bash
# Format code
black app/
ruff app/

# Type checking  
mypy app/

# Pre-commit hooks
pre-commit install
```

### Database Changes

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📝 API Documentation

- **Interactive Docs**: http://localhost:8000/docs (development only)
- **ReDoc**: http://localhost:8000/redoc (development only)
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## 🌟 Key Implementation Notes

- **Async Throughout**: Full async/await pattern for maximum performance
- **Modern SQLAlchemy**: Uses 2.0 syntax with async sessions
- **Comprehensive Caching**: Multi-layer caching with appropriate TTLs
- **Growth Simulation**: Sophisticated algorithms considering multiple factors
- **Privacy by Design**: Minimal data collection with automatic cleanup
- **Extensible**: Plugin-friendly architecture for new integrations
- **Production Ready**: Comprehensive error handling, logging, and monitoring

## 📚 Architecture Decisions

- **FastAPI**: Modern, fast, with excellent async support and automatic OpenAPI
- **PostgreSQL**: Robust ACID compliance, excellent JSON support, UUID native support
- **Redis**: High performance caching and message broker
- **Celery**: Mature, reliable background task processing
- **Pydantic**: Runtime type validation and serialization
- **Alembic**: Database migrations with rollback support
- **Docker**: Consistent deployment across environments