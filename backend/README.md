# Digital Greenhouse Backend API

A streamlined FastAPI backend powering an interactive 3D personal portfolio site with real-time growth simulation, weather systems, and visitor analytics.

## 🌱 Features

- **Garden State Management**: Dynamic 3D positioning and growth stages for projects
- **Real-time Growth Simulation**: Projects evolve based on GitHub activity and visitor engagement
- **Weather System**: Mood-based atmospheric conditions influenced by coding activity and music
- **Skills Constellation**: Interactive skill visualization with connection mapping
- **Visitor Analytics**: Privacy-focused engagement tracking and behavioral analysis
- **WebSocket Updates**: Real-time garden state synchronization
- **Background Tasks**: Lightweight asyncio-based task scheduling
- **Caching Layer**: In-memory caching for optimal performance
- **External Integrations**: Optional GitHub integration with sample data fallback

## 🏗️ Simple Architecture

- **FastAPI**: Async Python web framework
- **SQLite**: Lightweight database (no setup required!)
- **In-Memory Caching**: Zero-config caching system
- **Asyncio Tasks**: Built-in background processing
- **SQLAlchemy 2.0**: Modern async ORM
- **Sample Data**: Rich demo data when GitHub not configured

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (that's it!)

### Super Simple Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run the server**:
   ```bash
   python run_dev.py
   ```

3. **That's it!** 🎉
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

The system will:
- ✅ Create SQLite database automatically
- ✅ Generate rich sample data on first run
- ✅ Start background tasks for growth simulation
- ✅ Enable real-time WebSocket updates

### Optional Configuration

Create `.env` file for GitHub integration:
```bash
cp .env.example .env
# Edit .env to add your GitHub token (optional)
```

**Without GitHub token**: Uses rich sample data
**With GitHub token**: Syncs real repository data

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

Key environment variables (all optional):

```bash
# Application Security
SECRET_KEY=your-secret-key-here
ADMIN_PASSWORD=your-admin-password

# External APIs (optional)
GITHUB_TOKEN=your-github-token
GITHUB_USERNAME=your-github-username

# Features (defaults to true)
ENABLE_GITHUB_INTEGRATION=true
ENABLE_WEBSOCKETS=true
ENABLE_ANALYTICS=true
ENABLE_BACKGROUND_TASKS=true
```

See `.env.example` for complete configuration options.

## 🎯 Background Tasks

The system runs lightweight asyncio background tasks:

- **Growth Calculation**: Updates project growth stages every 15 minutes
- **Weather Updates**: Refreshes garden weather based on activity  
- **Data Synchronization**: Syncs from GitHub API when configured
- **Analytics Processing**: Built-in visitor behavior insights
- **Sample Data**: Auto-generates demo data on first run

All tasks run in-process with zero external dependencies!

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
- **Metrics**: `/metrics` endpoint with background task status
- **Admin Controls**: Manual task triggers at `/admin/tasks/*`
- **Sample Data**: Refresh demo data at `/admin/sample-data/refresh`
- **Logging**: Structured logging with configurable levels

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
- **In-Memory Caching**: Zero-config caching with TTL support
- **Growth Simulation**: Sophisticated algorithms considering multiple factors
- **Privacy by Design**: Minimal data collection with automatic cleanup
- **Zero Setup**: Works immediately with no external dependencies
- **Production Ready**: Comprehensive error handling, logging, and monitoring

## 📚 Architecture Decisions

- **FastAPI**: Modern, fast, with excellent async support and automatic OpenAPI
- **SQLite**: Zero-config, file-based database perfect for single-instance deployments
- **In-Memory Cache**: Eliminates Redis dependency while maintaining performance
- **Asyncio Tasks**: Built-in Python task scheduling replaces Celery complexity
- **Pydantic**: Runtime type validation and serialization
- **Sample Data**: Rich demo content eliminates external API dependencies
- **Single Binary**: Everything runs in one process for maximum simplicity