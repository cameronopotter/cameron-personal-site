"""
Weather state models for mood and atmosphere tracking
"""

from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Boolean,
    CheckConstraint, Index, func
)
from sqlalchemy.dialects.postgresql import UUID
from .base import Base, BaseModel


class WeatherState(Base, BaseModel):
    """
    Garden weather system for mood and atmosphere tracking
    Influenced by coding activity, music, time of day, and real weather
    """
    __tablename__ = "weather_states"

    # Weather classification
    weather_type = Column(String(50))    # 'sunny', 'stormy', 'cloudy', 'aurora', 'starry', 'misty', 'rainbow'
    intensity = Column(Float, CheckConstraint("intensity >= 0 AND intensity <= 1"))

    # Data sources that influenced this weather calculation
    github_commits_today = Column(Integer, default=0)
    coding_hours_today = Column(Float, default=0.0)
    music_mood = Column(String(50))          # from Spotify API: 'energetic', 'calm', 'focused', etc.
    actual_weather = Column(String(50))      # real weather influence from external API

    # Derived emotional and productivity indicators
    productivity_score = Column(Float, CheckConstraint("productivity_score >= 0 AND productivity_score <= 1"))
    creativity_index = Column(Float, CheckConstraint("creativity_index >= 0 AND creativity_index <= 1"))
    stress_level = Column(Float, CheckConstraint("stress_level >= 0 AND stress_level <= 1"))

    # Temporal context
    time_of_day = Column(String(20))         # 'dawn', 'day', 'dusk', 'night'
    season = Column(String(20))              # 'spring', 'summer', 'autumn', 'winter'

    # Weather state duration tracking
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))

    # Constraints and indexes
    __table_args__ = (
        CheckConstraint("weather_type IN ('sunny', 'stormy', 'cloudy', 'aurora', 'starry', 'misty', 'rainbow', 'twilight')", name='check_weather_type'),
        CheckConstraint("time_of_day IN ('dawn', 'day', 'dusk', 'night')", name='check_time_of_day'),
        CheckConstraint("season IN ('spring', 'summer', 'autumn', 'winter')", name='check_season'),
        CheckConstraint("started_at <= ended_at", name='check_weather_duration'),
        Index('idx_weather_states_started', 'started_at'),
        Index('idx_weather_states_type', 'weather_type'),
        Index('idx_weather_states_time_of_day', 'time_of_day'),
        Index('idx_weather_states_active', 'started_at', 'ended_at'),  # For finding current weather
    )

    def __repr__(self):
        return f"<WeatherState(weather_type='{self.weather_type}', intensity={self.intensity}, time_of_day='{self.time_of_day}')>"

    @property
    def is_active(self) -> bool:
        """Check if this weather state is currently active"""
        return self.ended_at is None

    @property
    def duration_minutes(self) -> float:
        """Calculate duration of weather state in minutes"""
        if self.ended_at:
            delta = self.ended_at - self.started_at
            return delta.total_seconds() / 60
        else:
            # Current ongoing weather
            from datetime import datetime
            delta = datetime.utcnow() - self.started_at
            return delta.total_seconds() / 60