"""
Global test configuration and fixtures for the Digital Greenhouse backend tests.
"""

import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator, Dict, Any
from unittest.mock import Mock, AsyncMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import redis.asyncio as redis
from httpx import AsyncClient
import faker

# Import app components
from app.main import app
from app.core.database import get_db, Base
from app.core.config import get_settings
from app.models import *
from app.integrations.websocket_manager import WebSocketManager

# Test configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_REDIS_URL = "redis://localhost:6379/1"

fake = faker.Faker()

# Global test settings
@pytest.fixture(scope="session")
def test_settings():
    """Override settings for testing."""
    settings = get_settings()
    settings.database_url = TEST_DATABASE_URL
    settings.redis_url = TEST_REDIS_URL
    settings.testing = True
    settings.log_level = "DEBUG"
    return settings

# Database fixtures
@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(
        "sqlite:///test.db",
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
        echo=False,
    )
    
    # Enable foreign key support for SQLite
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    return engine

@pytest_asyncio.fixture(scope="session")
async def async_engine():
    """Create async test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    return engine

@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for each test."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session

@pytest.fixture(scope="function")
def db_session(engine) -> Generator:
    """Create database session for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# FastAPI test client fixtures
@pytest.fixture(scope="function")
def client(db_session, test_settings) -> Generator[TestClient, None, None]:
    """Create FastAPI test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def async_client(async_session, test_settings) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    async def override_get_db():
        yield async_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

# Redis fixtures
@pytest_asyncio.fixture
async def redis_client():
    """Create Redis client for testing."""
    client = redis.from_url(TEST_REDIS_URL, decode_responses=True)
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.close()

# WebSocket fixtures
@pytest.fixture
def ws_manager():
    """Create WebSocket manager for testing."""
    manager = WebSocketManager()
    return manager

@pytest.fixture
def mock_websocket():
    """Create mock WebSocket connection."""
    mock_ws = Mock()
    mock_ws.send_text = AsyncMock()
    mock_ws.send_json = AsyncMock()
    mock_ws.receive_text = AsyncMock()
    mock_ws.receive_json = AsyncMock()
    mock_ws.close = AsyncMock()
    return mock_ws

# Data fixtures
@pytest.fixture
def sample_project_data():
    """Generate sample project data."""
    return {
        "name": fake.sentence(nb_words=3)[:-1],  # Remove period
        "description": fake.text(max_nb_chars=200),
        "github_url": f"https://github.com/{fake.user_name()}/{fake.slug()}",
        "live_url": fake.url(),
        "technologies": [fake.word() for _ in range(3)],
        "status": "active",
        "created_at": fake.date_time_this_year()
    }

@pytest.fixture
def sample_skill_data():
    """Generate sample skill data."""
    return {
        "name": fake.word().title(),
        "category": fake.random_element(['frontend', 'backend', 'database', 'devops']),
        "level": fake.random_int(min=1, max=100),
        "years_experience": fake.random_int(min=0, max=10),
        "last_used": fake.date_this_year()
    }

@pytest.fixture
def sample_visitor_data():
    """Generate sample visitor data."""
    return {
        "ip_address": fake.ipv4(),
        "user_agent": fake.user_agent(),
        "country": fake.country_code(),
        "city": fake.city(),
        "session_duration": fake.random_int(min=30, max=3600),
        "pages_viewed": fake.random_int(min=1, max=20)
    }

# Mock external services
@pytest.fixture
def mock_github_service():
    """Mock GitHub service."""
    mock = Mock()
    mock.get_repositories = AsyncMock(return_value=[
        {
            "name": "test-repo",
            "description": "Test repository",
            "url": "https://github.com/user/test-repo",
            "stars": 10,
            "forks": 5,
            "language": "Python"
        }
    ])
    mock.get_user_stats = AsyncMock(return_value={
        "public_repos": 25,
        "followers": 50,
        "following": 30
    })
    return mock

@pytest.fixture
def mock_weather_service():
    """Mock weather service."""
    mock = Mock()
    mock.get_current_weather = AsyncMock(return_value={
        "condition": "sunny",
        "temperature": 22.5,
        "humidity": 65,
        "wind_speed": 8.2,
        "pressure": 1013.25
    })
    return mock

@pytest.fixture
def mock_spotify_service():
    """Mock Spotify service."""
    mock = Mock()
    mock.get_currently_playing = AsyncMock(return_value={
        "track_name": "Test Song",
        "artist": "Test Artist",
        "album": "Test Album",
        "is_playing": True,
        "progress": 120000,
        "duration": 240000
    })
    return mock

@pytest.fixture
def mock_wakatime_service():
    """Mock WakaTime service."""
    mock = Mock()
    mock.get_stats = AsyncMock(return_value={
        "total_seconds": 86400,
        "languages": [
            {"name": "Python", "percent": 45.2, "total_seconds": 39000},
            {"name": "TypeScript", "percent": 35.8, "total_seconds": 30900}
        ],
        "projects": [
            {"name": "Digital Greenhouse", "percent": 75.0, "total_seconds": 64800}
        ]
    })
    return mock

# Performance testing fixtures
@pytest.fixture
def performance_monitor():
    """Create performance monitoring context."""
    import time
    import psutil
    import threading
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.start_memory = None
            self.end_memory = None
            self.cpu_percent = []
            self.monitoring = False
            self.monitor_thread = None
        
        def start(self):
            self.start_time = time.time()
            self.start_memory = psutil.Process().memory_info().rss
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_cpu)
            self.monitor_thread.start()
        
        def stop(self):
            self.end_time = time.time()
            self.end_memory = psutil.Process().memory_info().rss
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join()
        
        def _monitor_cpu(self):
            while self.monitoring:
                self.cpu_percent.append(psutil.cpu_percent())
                time.sleep(0.1)
        
        @property
        def duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
        
        @property
        def memory_delta(self):
            if self.start_memory and self.end_memory:
                return self.end_memory - self.start_memory
            return None
        
        @property
        def avg_cpu_percent(self):
            return sum(self.cpu_percent) / len(self.cpu_percent) if self.cpu_percent else 0
    
    return PerformanceMonitor()

# Event loop configuration for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Test data cleanup
@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Clean up temporary files after each test."""
    temp_files = []
    
    def create_temp_file(suffix=".tmp"):
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        temp_files.append(path)
        return path
    
    yield create_temp_file
    
    # Cleanup
    for file_path in temp_files:
        try:
            os.unlink(file_path)
        except FileNotFoundError:
            pass

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "db: Database tests")
    config.addinivalue_line("markers", "ws: WebSocket tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "external: Tests requiring external services")

def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark API tests
        if "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        
        # Mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Mark performance tests
        if "performance" in item.name or "perf" in item.name:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        
        # Mark external service tests
        if any(service in item.name for service in ["github", "spotify", "weather", "wakatime"]):
            item.add_marker(pytest.mark.external)