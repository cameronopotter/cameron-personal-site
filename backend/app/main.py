"""
Digital Greenhouse FastAPI Application
Main application entry point with comprehensive setup
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GzipMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from typing import Dict, Any

from app.core.config import settings
from app.core.database import init_database, close_database, check_database_connection
from app.core.cache import cache_manager
from app.api import api_router

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
        
        # Initialize Redis cache
        await cache_manager.connect()
        
        # Check all connections
        db_healthy = await check_database_connection()
        cache_healthy = await cache_manager.redis.ping() if cache_manager.redis else False
        
        if not db_healthy:
            raise Exception("Database connection failed")
        
        if not cache_healthy:
            logger.warning("Redis connection failed - caching will be disabled")
        
        logger.info("🚀 Digital Greenhouse API startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🌅 Digital Greenhouse API shutting down...")
    
    try:
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
    GzipMiddleware,
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
    
    # Check Redis cache
    try:
        if cache_manager.redis:
            cache_healthy = await cache_manager.redis.ping()
            health_status["components"]["cache"] = {
                "status": "healthy" if cache_healthy else "unhealthy",
                "details": "Redis connection verified" if cache_healthy else "Redis connection failed"
            }
        else:
            health_status["components"]["cache"] = {
                "status": "disabled",
                "details": "Redis not configured"
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
                "websockets": settings.enable_websockets
            }
        }
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