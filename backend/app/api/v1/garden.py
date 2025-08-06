"""
Garden management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
import logging

from app.core.database import get_async_db
from app.core.cache import cache_manager, CacheKeys, CacheTTL, cached
from app.models.projects import Project, ProjectGrowthLog
from app.models.skills import Skill
from app.models.weather import WeatherState
from app.models.visitors import VisitorSession
from app.schemas.garden import (
    GardenState, GardenSummaryResponse, GardenEvolution,
    GardenInteractionSuggestion, GardenHealth
)
from app.schemas.projects import SeedPlantingRequest, PlantedSeedResponse, GrowthStage
from app.schemas.weather import WeatherStateResponse
from app.services.garden import GardenService
from app.services.visitor_tracking import get_or_create_visitor_session

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=GardenState)
async def get_garden_state(
    season: Optional[str] = Query(None, description="Filter by season"),
    weather_type: Optional[str] = Query(None, description="Filter by weather type"),  
    visitor_session: str = Depends(get_or_create_visitor_session),
    db: AsyncSession = Depends(get_async_db)
) -> GardenState:
    """
    Get the complete garden ecosystem state including:
    - All projects with current growth stages
    - Active weather conditions  
    - Skill constellation positions
    - Personalized content based on visitor history
    """
    try:
        # Generate cache key with personalization
        cache_key = CacheKeys.garden_state(
            season=season or "",
            weather=weather_type or "",
            visitor_hash=visitor_session[:8]  # Use first 8 chars for privacy
        )
        
        # Try to get from cache first
        cached_state = await cache_manager.get(cache_key)
        if cached_state:
            logger.debug(f"Garden state served from cache for session {visitor_session[:8]}")
            return GardenState(**cached_state)
        
        # Get garden service
        garden_service = GardenService(db)
        
        # Build garden state
        garden_state = await garden_service.get_complete_garden_state(
            season=season,
            weather_type=weather_type,
            visitor_session=visitor_session
        )
        
        # Cache the result
        await cache_manager.set(
            cache_key,
            garden_state.dict(),
            CacheTTL.GARDEN_STATE
        )
        
        logger.info(f"Garden state generated and cached for session {visitor_session[:8]}")
        return garden_state
    
    except Exception as e:
        logger.error(f"Error getting garden state: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve garden state")


@router.get("/summary", response_model=GardenSummaryResponse)
async def get_garden_summary(
    db: AsyncSession = Depends(get_async_db)
) -> GardenSummaryResponse:
    """
    Get condensed garden overview for quick loading
    """
    try:
        cache_key = "garden:summary"
        
        # Try cache first
        cached_summary = await cache_manager.get(cache_key)
        if cached_summary:
            return GardenSummaryResponse(**cached_summary)
        
        garden_service = GardenService(db)
        summary = await garden_service.get_garden_summary()
        
        # Cache for shorter time since it's lighter data
        await cache_manager.set(
            cache_key,
            summary.dict(),
            CacheTTL.GARDEN_STATE // 2  # 2.5 minutes
        )
        
        return summary
    
    except Exception as e:
        logger.error(f"Error getting garden summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve garden summary")


@router.post("/plant-seed", response_model=PlantedSeedResponse)
async def plant_seed(
    seed_request: SeedPlantingRequest,
    background_tasks: BackgroundTasks,
    visitor_session: str = Depends(get_or_create_visitor_session),
    db: AsyncSession = Depends(get_async_db)
) -> PlantedSeedResponse:
    """
    Plant a new project seed at specified 3D coordinates
    Triggers growth simulation and analytics tracking
    """
    try:
        garden_service = GardenService(db)
        
        # Plant the seed
        planted_response = await garden_service.plant_project_seed(
            seed_request=seed_request,
            visitor_session=visitor_session
        )
        
        # Schedule background tasks
        background_tasks.add_task(
            garden_service.trigger_growth_calculation,
            planted_response.project.id
        )
        
        # Invalidate garden cache
        await cache_manager.clear_pattern("garden:*")
        
        logger.info(f"Seed planted: {planted_response.project.name} by session {visitor_session[:8]}")
        return planted_response
    
    except Exception as e:
        logger.error(f"Error planting seed: {e}")
        raise HTTPException(status_code=500, detail="Failed to plant seed")


@router.get("/weather", response_model=WeatherStateResponse)
async def get_current_weather(
    db: AsyncSession = Depends(get_async_db)
) -> WeatherStateResponse:
    """
    Get current garden weather influenced by:
    - Recent GitHub activity
    - Music listening patterns  
    - Time of day/season
    - Real weather data
    """
    try:
        cache_key = CacheKeys.weather_current()
        
        # Try cache first
        cached_weather = await cache_manager.get(cache_key)
        if cached_weather:
            return WeatherStateResponse(**cached_weather)
        
        # Get current weather from database
        result = await db.execute(
            select(WeatherState)
            .where(WeatherState.ended_at.is_(None))
            .order_by(WeatherState.started_at.desc())
            .limit(1)
        )
        current_weather = result.scalar_one_or_none()
        
        if not current_weather:
            raise HTTPException(status_code=404, detail="No current weather state found")
        
        weather_response = WeatherStateResponse.model_validate(current_weather)
        
        # Cache the weather
        await cache_manager.set(
            cache_key,
            weather_response.dict(),
            CacheTTL.WEATHER_STATE
        )
        
        return weather_response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current weather: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve weather")


@router.get("/evolution", response_model=GardenEvolution)
async def get_garden_evolution(
    db: AsyncSession = Depends(get_async_db)
) -> GardenEvolution:
    """
    Get garden evolution and growth timeline
    """
    try:
        cache_key = "garden:evolution"
        
        cached_evolution = await cache_manager.get(cache_key)
        if cached_evolution:
            return GardenEvolution(**cached_evolution)
        
        garden_service = GardenService(db)
        evolution = await garden_service.get_garden_evolution()
        
        # Cache for longer since evolution data changes slowly
        await cache_manager.set(
            cache_key,
            evolution.dict(),
            CacheTTL.ANALYTICS_DASHBOARD
        )
        
        return evolution
    
    except Exception as e:
        logger.error(f"Error getting garden evolution: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve garden evolution")


@router.get("/suggestions", response_model=List[GardenInteractionSuggestion])
async def get_interaction_suggestions(
    visitor_session: str = Depends(get_or_create_visitor_session),
    db: AsyncSession = Depends(get_async_db)
) -> List[GardenInteractionSuggestion]:
    """
    Get personalized interaction suggestions for visitors
    """
    try:
        cache_key = f"garden:suggestions:{visitor_session[:8]}"
        
        cached_suggestions = await cache_manager.get(cache_key)
        if cached_suggestions:
            return [GardenInteractionSuggestion(**s) for s in cached_suggestions]
        
        garden_service = GardenService(db)
        suggestions = await garden_service.get_interaction_suggestions(visitor_session)
        
        # Cache suggestions for shorter time since they're personalized
        await cache_manager.set(
            cache_key,
            [s.dict() for s in suggestions],
            CacheTTL.VISITOR_SESSION // 2  # 30 minutes
        )
        
        return suggestions
    
    except Exception as e:
        logger.error(f"Error getting interaction suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve suggestions")


@router.get("/health", response_model=GardenHealth)
async def get_garden_health(
    db: AsyncSession = Depends(get_async_db)
) -> GardenHealth:
    """
    Get garden ecosystem health metrics and recommendations
    """
    try:
        cache_key = "garden:health"
        
        cached_health = await cache_manager.get(cache_key)
        if cached_health:
            return GardenHealth(**cached_health)
        
        garden_service = GardenService(db)
        health = await garden_service.calculate_garden_health()
        
        # Cache health metrics
        await cache_manager.set(
            cache_key,
            health.dict(),
            CacheTTL.ANALYTICS_DASHBOARD // 2  # 30 minutes
        )
        
        return health
    
    except Exception as e:
        logger.error(f"Error getting garden health: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve garden health")


@router.post("/refresh")
async def refresh_garden_cache(
    background_tasks: BackgroundTasks
) -> dict:
    """
    Manually refresh garden cache (admin endpoint)
    """
    try:
        # Clear all garden-related cache
        cleared_count = await cache_manager.clear_pattern("garden:*")
        
        logger.info(f"Garden cache refreshed, cleared {cleared_count} keys")
        return {
            "success": True,
            "message": f"Garden cache refreshed, cleared {cleared_count} cached items"
        }
    
    except Exception as e:
        logger.error(f"Error refreshing garden cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh cache")