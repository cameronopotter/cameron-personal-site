"""
Weather service for garden mood and atmosphere
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
import random

from app.models.weather import WeatherState
from app.schemas.weather import WeatherStateResponse, WeatherType, TimeOfDay, Season

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for managing garden weather states"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_current_weather(self) -> WeatherStateResponse:
        """Get current active weather state"""
        
        result = await self.db.execute(
            select(WeatherState)
            .where(WeatherState.ended_at.is_(None))
            .order_by(desc(WeatherState.started_at))
            .limit(1)
        )
        
        current_weather = result.scalar_one_or_none()
        
        if not current_weather:
            # Create default weather if none exists
            current_weather = await self._create_default_weather()
        
        return WeatherStateResponse.model_validate(current_weather)
    
    async def update_weather_conditions(
        self,
        github_commits: int = 0,
        coding_hours: float = 0.0,
        music_mood: Optional[str] = None,
        actual_weather: Optional[str] = None,
        force_change: bool = False
    ) -> WeatherStateResponse:
        """Update weather based on various factors"""
        
        # Get current weather
        current_weather = await self.get_current_weather()
        
        # Calculate new weather state
        new_weather_data = await self._calculate_weather_state(
            github_commits=github_commits,
            coding_hours=coding_hours,
            music_mood=music_mood,
            actual_weather=actual_weather
        )
        
        # Check if weather should change
        should_change = (
            force_change or
            self._significant_change_detected(current_weather.dict(), new_weather_data) or
            await self._is_weather_stale(current_weather.id)
        )
        
        if should_change:
            # End current weather
            await self._end_current_weather()
            
            # Create new weather state
            new_weather = await self._create_weather_state(new_weather_data)
            logger.info(f"Weather changed to {new_weather.weather_type} with intensity {new_weather.intensity}")
            return WeatherStateResponse.model_validate(new_weather)
        
        return current_weather
    
    async def get_weather_history(self, limit: int = 10) -> List[WeatherStateResponse]:
        """Get recent weather history"""
        
        result = await self.db.execute(
            select(WeatherState)
            .order_by(desc(WeatherState.started_at))
            .limit(limit)
        )
        
        weather_states = result.scalars().all()
        return [WeatherStateResponse.model_validate(w) for w in weather_states]
    
    async def get_weather_analytics(self, days_back: int = 7) -> Dict[str, Any]:
        """Get weather analytics for the specified period"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Weather type distribution
        result = await self.db.execute(
            select(WeatherState.weather_type, func.count(WeatherState.id))
            .where(WeatherState.started_at >= cutoff_date)
            .group_by(WeatherState.weather_type)
        )
        weather_distribution = dict(result.fetchall())
        
        # Average intensity by weather type
        result = await self.db.execute(
            select(WeatherState.weather_type, func.avg(WeatherState.intensity))
            .where(WeatherState.started_at >= cutoff_date)
            .group_by(WeatherState.weather_type)
        )
        intensity_by_type = dict(result.fetchall())
        
        # Weather patterns by time of day
        result = await self.db.execute(
            select(WeatherState.time_of_day, func.count(WeatherState.id))
            .where(WeatherState.started_at >= cutoff_date)
            .group_by(WeatherState.time_of_day)
        )
        time_patterns = dict(result.fetchall())
        
        # Productivity correlation
        result = await self.db.execute(
            select(func.avg(WeatherState.productivity_score))
            .where(
                and_(
                    WeatherState.started_at >= cutoff_date,
                    WeatherState.productivity_score.isnot(None)
                )
            )
        )
        avg_productivity = result.scalar() or 0
        
        return {
            "period_days": days_back,
            "weather_distribution": weather_distribution,
            "average_intensity_by_type": {k: float(v) for k, v in intensity_by_type.items()},
            "time_of_day_patterns": time_patterns,
            "average_productivity_score": float(avg_productivity)
        }
    
    # Helper methods
    async def _create_default_weather(self) -> WeatherState:
        """Create a default weather state"""
        
        weather = WeatherState(
            weather_type="sunny",
            intensity=0.5,
            time_of_day=self._get_current_time_of_day(),
            season=self._get_current_season(),
            productivity_score=0.5,
            creativity_index=0.5,
            stress_level=0.3
        )
        
        self.db.add(weather)
        await self.db.commit()
        await self.db.refresh(weather)
        
        return weather
    
    async def _calculate_weather_state(
        self,
        github_commits: int = 0,
        coding_hours: float = 0.0,
        music_mood: Optional[str] = None,
        actual_weather: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate new weather state based on input factors"""
        
        # Base weather calculation
        weather_type = "cloudy"
        intensity = 0.5
        productivity_score = 0.5
        creativity_index = 0.5
        stress_level = 0.3
        
        # GitHub activity influence
        if github_commits > 0:
            if github_commits >= 5:
                weather_type = "aurora"  # High activity
                intensity = min(0.8 + (github_commits * 0.02), 1.0)
                productivity_score = min(0.8 + (github_commits * 0.03), 1.0)
            elif github_commits >= 3:
                weather_type = "sunny"
                intensity = 0.7
                productivity_score = 0.7
            else:
                weather_type = "cloudy"
                intensity = 0.6
                productivity_score = 0.6
        
        # Coding hours influence
        if coding_hours > 0:
            if coding_hours >= 6:
                # Long coding session - might increase stress
                stress_level = min(0.7, stress_level + 0.3)
                if weather_type == "sunny":
                    weather_type = "stormy"  # Intense work
            elif coding_hours >= 3:
                productivity_score += 0.2
                creativity_index += 0.1
        
        # Music mood influence
        if music_mood:
            mood_effects = {
                "energetic": {"weather_type": "sunny", "intensity_boost": 0.2, "creativity_boost": 0.2},
                "calm": {"weather_type": "misty", "intensity_boost": -0.1, "stress_reduction": 0.2},
                "focused": {"weather_type": "starry", "intensity_boost": 0.1, "productivity_boost": 0.2},
                "creative": {"weather_type": "aurora", "intensity_boost": 0.3, "creativity_boost": 0.4},
                "melancholy": {"weather_type": "cloudy", "intensity_boost": -0.2, "stress_boost": 0.1}
            }
            
            if music_mood in mood_effects:
                effect = mood_effects[music_mood]
                weather_type = effect.get("weather_type", weather_type)
                intensity += effect.get("intensity_boost", 0)
                productivity_score += effect.get("productivity_boost", 0)
                creativity_index += effect.get("creativity_boost", 0)
                stress_level += effect.get("stress_boost", 0)
                stress_level -= effect.get("stress_reduction", 0)
        
        # Time of day influence
        time_of_day = self._get_current_time_of_day()
        if time_of_day == "night" and weather_type == "sunny":
            weather_type = "starry"
        elif time_of_day == "dawn" and weather_type not in ["aurora", "misty"]:
            weather_type = "misty"
        
        # Actual weather influence (subtle)
        if actual_weather:
            if "rain" in actual_weather.lower() and weather_type == "sunny":
                weather_type = "cloudy"
                intensity *= 0.8
            elif "clear" in actual_weather.lower():
                intensity = min(intensity + 0.1, 1.0)
        
        # Clamp values
        intensity = max(0.0, min(1.0, intensity))
        productivity_score = max(0.0, min(1.0, productivity_score))
        creativity_index = max(0.0, min(1.0, creativity_index))
        stress_level = max(0.0, min(1.0, stress_level))
        
        return {
            "weather_type": weather_type,
            "intensity": intensity,
            "github_commits_today": github_commits,
            "coding_hours_today": coding_hours,
            "music_mood": music_mood,
            "actual_weather": actual_weather,
            "productivity_score": productivity_score,
            "creativity_index": creativity_index,
            "stress_level": stress_level,
            "time_of_day": time_of_day,
            "season": self._get_current_season()
        }
    
    def _significant_change_detected(
        self,
        current_weather: Dict[str, Any],
        new_weather: Dict[str, Any]
    ) -> bool:
        """Check if weather change is significant enough"""
        
        # Weather type changed
        if current_weather.get("weather_type") != new_weather.get("weather_type"):
            return True
        
        # Significant intensity change
        intensity_diff = abs(
            current_weather.get("intensity", 0) - new_weather.get("intensity", 0)
        )
        if intensity_diff > 0.3:
            return True
        
        # Significant productivity change
        productivity_diff = abs(
            current_weather.get("productivity_score", 0) - new_weather.get("productivity_score", 0)
        )
        if productivity_diff > 0.4:
            return True
        
        return False
    
    async def _is_weather_stale(self, weather_id) -> bool:
        """Check if current weather has been active too long"""
        
        result = await self.db.execute(
            select(WeatherState.started_at)
            .where(WeatherState.id == weather_id)
        )
        started_at = result.scalar()
        
        if started_at:
            hours_active = (datetime.utcnow() - started_at).total_seconds() / 3600
            return hours_active > 4  # Weather is stale after 4 hours
        
        return True
    
    async def _end_current_weather(self):
        """End the current active weather state"""
        
        result = await self.db.execute(
            select(WeatherState)
            .where(WeatherState.ended_at.is_(None))
        )
        
        current_weather = result.scalar_one_or_none()
        if current_weather:
            current_weather.ended_at = datetime.utcnow()
            await self.db.commit()
    
    async def _create_weather_state(self, weather_data: Dict[str, Any]) -> WeatherState:
        """Create new weather state"""
        
        weather = WeatherState(**weather_data)
        self.db.add(weather)
        await self.db.commit()
        await self.db.refresh(weather)
        
        return weather
    
    def _get_current_time_of_day(self) -> str:
        """Determine current time of day"""
        hour = datetime.utcnow().hour
        
        if 5 <= hour < 12:
            return "dawn"
        elif 12 <= hour < 17:
            return "day"
        elif 17 <= hour < 20:
            return "dusk"
        else:
            return "night"
    
    def _get_current_season(self) -> str:
        """Determine current season"""
        month = datetime.utcnow().month
        
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "autumn"
        else:
            return "winter"