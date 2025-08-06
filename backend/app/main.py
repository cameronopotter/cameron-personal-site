"""
Digital Greenhouse FastAPI Application
Main application entry point with comprehensive setup
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from typing import Dict, Any

from app.core.config import settings
from app.core.database import init_database, close_database, check_database_connection
from app.core.cache import cache_manager
from app.api import api_router
from app.background_tasks import start_background_tasks, stop_background_tasks
from app.sample_data import init_sample_data

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🌱 Digital Greenhouse API starting up...")
    
    try:
        # Initialize database
        await init_database()
        
        # Initialize in-memory cache
        await cache_manager.connect()
        
        # Check database connection
        db_healthy = await check_database_connection()
        
        if not db_healthy:
            raise Exception("Database connection failed")
        
        # Initialize sample data if needed
        await init_sample_data()
        
        # Start background tasks
        await start_background_tasks()
        
        logger.info("🚀 Digital Greenhouse API startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🌅 Digital Greenhouse API shutting down...")
    
    try:
        await stop_background_tasks()
        await cache_manager.disconnect()
        await close_database()
        logger.info("👋 Digital Greenhouse API shutdown complete!")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "message": "An unexpected error occurred"
            }
        )


# Include API routes
app.include_router(api_router)

# Include WebSocket routes if enabled
if settings.enable_websockets:
    from app.websockets.garden_ws import router as ws_router
    app.include_router(ws_router)


# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    """API root endpoint with basic information"""
    return {
        "message": "🌱 Digital Greenhouse API",
        "version": settings.app_version,
        "status": "healthy",
        "features": {
            "garden_state": True,
            "project_growth": True,
            "skills_constellation": True,
            "weather_system": True,
            "visitor_analytics": settings.enable_analytics,
            "github_integration": settings.enable_github_integration,
            "spotify_integration": settings.enable_spotify_integration,
            "weather_integration": settings.enable_weather_integration,
            "websockets": settings.enable_websockets
        },
        "documentation": "/docs" if settings.debug else "Contact administrator"
    }


# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.app_version,
        "components": {}
    }
    
    # Check database
    try:
        db_healthy = await check_database_connection()
        health_status["components"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "details": "Connection verified" if db_healthy else "Connection failed"
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "details": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check in-memory cache
    try:
        cache_stats = await cache_manager.get_cache_stats()
        health_status["components"]["cache"] = {
            "status": "healthy",
            "details": f"In-memory cache active with {cache_stats.get('total_keys', 0)} keys"
        }
    except Exception as e:
        health_status["components"]["cache"] = {
            "status": "unhealthy",
            "details": str(e)
        }
        health_status["status"] = "degraded"
    
    # Overall status
    unhealthy_components = [
        comp for comp in health_status["components"].values()
        if comp["status"] == "unhealthy"
    ]
    
    if unhealthy_components:
        health_status["status"] = "unhealthy"
    
    return health_status


# Metrics endpoint (for monitoring systems)
@app.get("/metrics")
async def metrics() -> Dict[str, Any]:
    """Basic metrics endpoint for monitoring"""
    from app.background_tasks import get_all_tasks_status
    
    task_statuses = await get_all_tasks_status()
    
    return {
        "app_info": {
            "name": settings.app_name,
            "version": settings.app_version
        },
        "system_info": {
            "debug_mode": settings.debug,
            "features_enabled": {
                "analytics": settings.enable_analytics,
                "github": settings.enable_github_integration,
                "spotify": settings.enable_spotify_integration,
                "weather": settings.enable_weather_integration,
                "websockets": settings.enable_websockets,
                "background_tasks": settings.enable_background_tasks
            }
        },
        "background_tasks": {
            "total_tasks": len(task_statuses),
            "task_summary": {
                task_name: {
                    "status": result.status.value,
                    "last_run": result.completed_at.isoformat() if result.completed_at else None,
                    "duration": result.duration_seconds
                }
                for task_name, result in task_statuses.items()
            }
        }
    }


# Admin endpoints for manual task execution
@app.post("/admin/tasks/growth-calculation")
async def trigger_growth_calculation():
    """Manually trigger project growth calculation"""
    from app.background_tasks import execute_growth_calculation
    
    result = await execute_growth_calculation()
    return {
        "success": True,
        "task_name": result.task_name,
        "status": result.status.value,
        "started_at": result.started_at.isoformat()
    }


@app.post("/admin/tasks/weather-update")
async def trigger_weather_update():
    """Manually trigger weather update"""
    from app.background_tasks import execute_weather_update
    
    result = await execute_weather_update()
    return {
        "success": True,
        "task_name": result.task_name,
        "status": result.status.value,
        "started_at": result.started_at.isoformat()
    }


@app.post("/admin/tasks/data-sync")
async def trigger_data_sync():
    """Manually trigger external data sync"""
    from app.background_tasks import execute_data_sync
    
    result = await execute_data_sync()
    return {
        "success": True,
        "task_name": result.task_name,
        "status": result.status.value,
        "started_at": result.started_at.isoformat()
    }


@app.post("/admin/sample-data/refresh")
async def refresh_sample_data():
    """Refresh sample data (admin function)"""
    from app.sample_data import refresh_sample_data
    
    try:
        result = await refresh_sample_data()
        return {
            "success": True,
            "message": "Sample data refreshed successfully",
            "details": result
        }
    except Exception as e:
        logger.error(f"Error refreshing sample data: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Add startup banner
logger.info(f"""
🌱🌱🌱 Digital Greenhouse API 🌱🌱🌱
Version: {settings.app_version}
Debug Mode: {settings.debug}
Features: Garden State, Project Growth, Skills Constellation, Weather System
Integrations: GitHub{'✓' if settings.enable_github_integration else '✗'}, Spotify{'✓' if settings.enable_spotify_integration else '✗'}, Weather{'✓' if settings.enable_weather_integration else '✗'}
🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱🌱
""")