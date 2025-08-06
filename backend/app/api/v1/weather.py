"""
Weather API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.core.database import get_async_db
from app.core.cache import cache_manager, CacheKeys, CacheTTL
from app.schemas.weather import (
    WeatherStateResponse, MoodUpdateRequest, WeatherUpdateResponse
)
from app.services.weather import WeatherService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/current", response_model=WeatherStateResponse)
async def get_current_weather(
    db: AsyncSession = Depends(get_async_db)
) -> WeatherStateResponse:
    """Get current garden weather state"""
    
    try:
        cache_key = CacheKeys.weather_current()
        
        # Try cache first
        cached_weather = await cache_manager.get(cache_key)
        if cached_weather:
            return WeatherStateResponse(**cached_weather)
        
        weather_service = WeatherService(db)
        current_weather = await weather_service.get_current_weather()
        
        # Cache the weather
        await cache_manager.set(
            cache_key,
            current_weather.dict(),
            CacheTTL.WEATHER_STATE
        )
        
        return current_weather
    
    except Exception as e:
        logger.error(f"Error getting current weather: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve weather")


@router.post("/update-mood", response_model=WeatherUpdateResponse)
async def update_mood_weather(
    mood_data: MoodUpdateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
) -> WeatherUpdateResponse:
    """Update weather based on mood indicators"""
    
    try:
        weather_service = WeatherService(db)
        
        # Get current weather for comparison
        previous_weather = await weather_service.get_current_weather()
        
        # Update weather conditions
        current_weather = await weather_service.update_weather_conditions(
            music_mood=mood_data.music_mood,
            actual_weather=mood_data.external_weather,
            force_change=mood_data.force_weather_change
        )
        
        weather_changed = previous_weather.weather_type != current_weather.weather_type
        
        # Clear weather cache if changed
        if weather_changed:
            await cache_manager.delete(CacheKeys.weather_current())
            background_tasks.add_task(
                cache_manager.clear_pattern,
                "garden:*"  # Clear garden cache since weather affects it
            )
        
        return WeatherUpdateResponse(
            success=True,
            message="Weather updated successfully",
            weather_changed=weather_changed,
            previous_weather=previous_weather if weather_changed else None,
            current_weather=current_weather,
            change_reason="mood_update" if weather_changed else None
        )
    
    except Exception as e:
        logger.error(f"Error updating weather mood: {e}")
        raise HTTPException(status_code=500, detail="Failed to update weather")


@router.get("/history", response_model=List[WeatherStateResponse])
async def get_weather_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_async_db)
) -> List[WeatherStateResponse]:
    """Get recent weather history"""
    
    try:
        weather_service = WeatherService(db)
        history = await weather_service.get_weather_history(limit=limit)
        return history
    
    except Exception as e:
        logger.error(f"Error getting weather history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve weather history")


@router.get("/analytics")
async def get_weather_analytics(
    days_back: int = 7,
    db: AsyncSession = Depends(get_async_db)
) -> dict:
    """Get weather analytics for the specified period"""
    
    try:
        cache_key = f"weather:analytics:{days_back}d"
        
        # Try cache first
        cached_analytics = await cache_manager.get(cache_key)
        if cached_analytics:
            return cached_analytics
        
        weather_service = WeatherService(db)
        analytics = await weather_service.get_weather_analytics(days_back=days_back)
        
        # Cache analytics
        await cache_manager.set(
            cache_key,
            analytics,
            CacheTTL.ANALYTICS_DASHBOARD
        )
        
        return analytics
    
    except Exception as e:
        logger.error(f"Error getting weather analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve weather analytics")