"""
Weather mood engine for synthesizing atmospheric conditions from multiple data sources.
"""

import math
import colorsys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .spotify_service import SpotifyService, MoodAnalysis, MoodCategory
from .weather_service import WeatherService, AtmosphericMood, WeatherCondition
from .wakatime_service import WakaTimeService, ProductivityLevel
from .websocket_manager import websocket_manager, WebSocketEvent, EventType

import logging
logger = logging.getLogger(__name__)


class AtmosphereType(str, Enum):
    """Garden atmosphere types"""
    SERENE_MORNING = "serene_morning"
    ENERGETIC_NOON = "energetic_noon" 
    FOCUSED_AFTERNOON = "focused_afternoon"
    CREATIVE_EVENING = "creative_evening"
    CONTEMPLATIVE_NIGHT = "contemplative_night"
    STORMY_INTENSITY = "stormy_intensity"
    MISTY_MYSTERY = "misty_mystery"
    WINTER_CALM = "winter_calm"
    SPRING_GROWTH = "spring_growth"
    SUMMER_VITALITY = "summer_vitality"
    AUTUMN_REFLECTION = "autumn_reflection"


class WeatherPattern(str, Enum):
    """Synthesized weather patterns for the garden"""
    CLEAR_SKIES = "clear_skies"
    GENTLE_BREEZE = "gentle_breeze" 
    SOFT_RAIN = "soft_rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    MISTY_FOG = "misty_fog"
    SNOW_FALL = "snow_fall"
    AURORA_LIGHTS = "aurora_lights"  # Special coding achievement effect
    RAINBOW = "rainbow"              # Special mood combination effect


@dataclass
class MoodSynthesis:
    """Synthesized mood from all data sources"""
    primary_atmosphere: AtmosphereType
    weather_pattern: WeatherPattern
    
    # Mood components (0.0 to 1.0)
    energy_level: float
    focus_level: float
    creativity_level: float
    serenity_level: float
    intensity_level: float
    
    # Visual properties
    color_palette: List[str]  # Hex colors
    lighting_style: str
    particle_density: float   # 0.0 to 1.0
    wind_strength: float      # 0.0 to 1.0
    
    # Audio properties
    ambient_sounds: List[str]
    music_influence: float    # How much music affects the mood
    
    # Growth modifiers
    growth_rate_modifier: float  # 0.5 to 2.0
    bloom_probability: float     # 0.0 to 1.0
    
    # Metadata
    confidence: float         # 0.0 to 1.0
    data_sources: List[str]   # Which services contributed
    last_updated: datetime
    transitions: Dict[str, float]  # Transition timing for smooth changes


@dataclass
class MoodTransition:
    """Smooth transition between mood states"""
    from_mood: MoodSynthesis
    to_mood: MoodSynthesis
    duration_seconds: int
    easing_function: str  # "linear", "ease_in", "ease_out", "ease_in_out"
    start_time: datetime


class MoodEngine:
    """Weather mood synthesis engine"""
    
    def __init__(self):
        self.spotify_service = SpotifyService()
        self.weather_service = WeatherService()
        self.wakatime_service = WakaTimeService()
        
        # Current mood state
        self.current_mood: Optional[MoodSynthesis] = None
        self.mood_history: List[MoodSynthesis] = []
        self.active_transition: Optional[MoodTransition] = None
        
        # Synthesis weights
        self.source_weights = {
            "music": 0.4,      # Music has strong influence on mood
            "weather": 0.3,    # Weather sets base atmosphere
            "productivity": 0.2, # Work state affects energy
            "time_of_day": 0.1  # Time context
        }
        
        # Color palettes for different moods
        self.color_palettes = {
            "energetic": ["#FF6B6B", "#FFE066", "#4ECDC4", "#45B7D1"],
            "serene": ["#96CEB4", "#FFEAA7", "#DDA0DD", "#87CEEB"], 
            "focused": ["#6C5CE7", "#A29BFE", "#74B9FF", "#00B894"],
            "creative": ["#FD79A8", "#FDCB6E", "#6C5CE7", "#00CECA"],
            "contemplative": ["#636E72", "#B2BEC3", "#DDA0DD", "#81ECEC"],
            "intense": ["#E17055", "#FDCB6E", "#E84393", "#00B894"]
        }
    
    async def synthesize_current_mood(self) -> MoodSynthesis:
        """Synthesize current mood from all available data sources"""
        try:
            data_sources = []
            
            # Gather data from all sources
            music_data = await self._get_music_mood()
            weather_data = await self._get_weather_mood()
            productivity_data = await self._get_productivity_mood()
            time_context = self._get_time_context()
            
            # Track which sources provided data
            if music_data:
                data_sources.append("spotify")
            if weather_data:
                data_sources.append("weather")
            if productivity_data:
                data_sources.append("wakatime")
            data_sources.append("time")
            
            # Synthesize mood components
            mood_components = self._blend_mood_components(
                music_data, weather_data, productivity_data, time_context
            )
            
            # Determine primary atmosphere
            primary_atmosphere = self._determine_primary_atmosphere(mood_components)
            
            # Determine weather pattern
            weather_pattern = self._determine_weather_pattern(mood_components, weather_data)
            
            # Generate visual properties
            visual_props = self._generate_visual_properties(mood_components, primary_atmosphere)
            
            # Generate audio properties  
            audio_props = self._generate_audio_properties(mood_components, music_data)
            
            # Calculate growth modifiers
            growth_modifiers = self._calculate_growth_modifiers(mood_components)
            
            # Calculate confidence
            confidence = self._calculate_synthesis_confidence(data_sources)
            
            # Create synthesized mood
            synthesized_mood = MoodSynthesis(
                primary_atmosphere=primary_atmosphere,
                weather_pattern=weather_pattern,
                energy_level=mood_components["energy"],
                focus_level=mood_components["focus"], 
                creativity_level=mood_components["creativity"],
                serenity_level=mood_components["serenity"],
                intensity_level=mood_components["intensity"],
                color_palette=visual_props["colors"],
                lighting_style=visual_props["lighting"],
                particle_density=visual_props["particles"],
                wind_strength=visual_props["wind"],
                ambient_sounds=audio_props["sounds"],
                music_influence=audio_props["music_influence"],
                growth_rate_modifier=growth_modifiers["rate"],
                bloom_probability=growth_modifiers["bloom"],
                confidence=confidence,
                data_sources=data_sources,
                last_updated=datetime.utcnow(),
                transitions=self._calculate_transition_timings(mood_components)
            )
            
            # Check for significant mood changes
            await self._handle_mood_change(synthesized_mood)
            
            # Update state
            if self.current_mood:
                self.mood_history.append(self.current_mood)
                if len(self.mood_history) > 100:  # Keep last 100 moods
                    self.mood_history.pop(0)
            
            self.current_mood = synthesized_mood
            
            return synthesized_mood
            
        except Exception as e:
            logger.error(f"Failed to synthesize mood: {e}")
            return self._get_default_mood()
    
    async def _get_music_mood(self) -> Optional[Dict[str, Any]]:
        """Get current music mood data"""
        try:
            if not self.spotify_service.is_available():
                return None
            
            mood_response = await self.spotify_service.analyze_current_mood()
            if not mood_response.success or not mood_response.data:
                return None
            
            mood_analysis = mood_response.data
            
            return {
                "primary_mood": mood_analysis.primary_mood,
                "energy": mood_analysis.energy_level,
                "positivity": mood_analysis.positivity_level,
                "intensity": mood_analysis.intensity_level,
                "focus": mood_analysis.focus_level,
                "weather_influence": mood_analysis.weather_influence,
                "confidence": mood_analysis.confidence
            }
            
        except Exception as e:
            logger.warning(f"Failed to get music mood: {e}")
            return None
    
    async def _get_weather_mood(self) -> Optional[Dict[str, Any]]:
        """Get weather-based mood data"""
        try:
            if not self.weather_service.is_available():
                return None
            
            weather_response = await self.weather_service.get_current_weather()
            if not weather_response.success:
                return None
            
            current_weather = weather_response.data
            atmospheric_mood = self.weather_service.analyze_atmospheric_mood(current_weather)
            seasonal_influence = self.weather_service.calculate_seasonal_influence()
            
            return {
                "condition": current_weather.condition,
                "temperature": current_weather.temperature,
                "mood": atmospheric_mood.primary_mood,
                "intensity": atmospheric_mood.intensity,
                "colors": atmospheric_mood.color_palette,
                "lighting": atmospheric_mood.lighting_style,
                "particles": atmospheric_mood.particle_effects,
                "growth_modifier": atmospheric_mood.growth_modifier,
                "season": seasonal_influence.season,
                "growth_factor": seasonal_influence.growth_factor
            }
            
        except Exception as e:
            logger.warning(f"Failed to get weather mood: {e}")
            return None
    
    async def _get_productivity_mood(self) -> Optional[Dict[str, Any]]:
        """Get productivity-based mood data"""
        try:
            if not self.wakatime_service.is_available():
                return None
            
            productivity_response = await self.wakatime_service.get_productivity_analysis(7)
            if not productivity_response.success:
                return None
            
            productivity = productivity_response.data
            
            # Map productivity to mood components
            level_mapping = {
                ProductivityLevel.VERY_HIGH: {"energy": 0.9, "focus": 0.9, "intensity": 0.8},
                ProductivityLevel.HIGH: {"energy": 0.7, "focus": 0.8, "intensity": 0.6}, 
                ProductivityLevel.MODERATE: {"energy": 0.5, "focus": 0.6, "intensity": 0.4},
                ProductivityLevel.LOW: {"energy": 0.3, "focus": 0.4, "intensity": 0.2},
                ProductivityLevel.VERY_LOW: {"energy": 0.1, "focus": 0.2, "intensity": 0.1}
            }
            
            mood_values = level_mapping.get(productivity.current_level, {"energy": 0.5, "focus": 0.5, "intensity": 0.3})
            
            return {
                "level": productivity.current_level,
                "energy": mood_values["energy"],
                "focus": mood_values["focus"], 
                "intensity": mood_values["intensity"],
                "consistency": productivity.consistency_score,
                "weekly_hours": productivity.weekly_hours
            }
            
        except Exception as e:
            logger.warning(f"Failed to get productivity mood: {e}")
            return None
    
    def _get_time_context(self) -> Dict[str, Any]:
        """Get time-of-day context for mood"""
        now = datetime.utcnow()
        hour = now.hour
        
        # Define time periods
        if 5 <= hour < 9:
            period = "morning"
            energy_base = 0.6
            serenity_base = 0.7
        elif 9 <= hour < 12:
            period = "late_morning"
            energy_base = 0.8
            serenity_base = 0.5
        elif 12 <= hour < 14:
            period = "noon"
            energy_base = 0.9
            serenity_base = 0.4
        elif 14 <= hour < 17:
            period = "afternoon"
            energy_base = 0.7
            serenity_base = 0.4
        elif 17 <= hour < 20:
            period = "evening"
            energy_base = 0.5
            serenity_base = 0.6
        elif 20 <= hour < 23:
            period = "night"
            energy_base = 0.3
            serenity_base = 0.8
        else:  # 23-5
            period = "late_night"
            energy_base = 0.2
            serenity_base = 0.9
        
        return {
            "period": period,
            "hour": hour,
            "energy": energy_base,
            "serenity": serenity_base,
            "focus": 0.6 if 9 <= hour <= 17 else 0.4  # Higher focus during work hours
        }
    
    def _blend_mood_components(
        self,
        music_data: Optional[Dict[str, Any]],
        weather_data: Optional[Dict[str, Any]], 
        productivity_data: Optional[Dict[str, Any]],
        time_context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Blend mood components from all sources"""
        
        # Initialize with time-based defaults
        components = {
            "energy": time_context["energy"],
            "focus": time_context["focus"],
            "creativity": 0.5,
            "serenity": time_context["serenity"],
            "intensity": 0.3
        }
        
        weights_sum = self.source_weights["time_of_day"]
        
        # Blend music influence
        if music_data:
            weight = self.source_weights["music"]
            components["energy"] += music_data["energy"] * weight
            components["focus"] += music_data["focus"] * weight
            components["intensity"] += music_data["intensity"] * weight
            
            # Music creativity mapping
            if music_data["primary_mood"] in [MoodCategory.CREATIVE, MoodCategory.DREAMY]:
                components["creativity"] += 0.8 * weight
            elif music_data["primary_mood"] == MoodCategory.FOCUSED:
                components["creativity"] += 0.4 * weight
            
            # Serenity from music
            if music_data["primary_mood"] == MoodCategory.CALM:
                components["serenity"] += 0.9 * weight
            elif music_data["primary_mood"] == MoodCategory.MELANCHOLIC:
                components["serenity"] += 0.6 * weight
            
            weights_sum += weight
        
        # Blend weather influence
        if weather_data:
            weight = self.source_weights["weather"]
            components["intensity"] += weather_data["intensity"] * weight
            
            # Weather-specific mood adjustments
            if weather_data["condition"] in [WeatherCondition.CLEAR, WeatherCondition.CLOUDS]:
                components["serenity"] += 0.7 * weight
                components["energy"] += 0.6 * weight
            elif weather_data["condition"] in [WeatherCondition.RAIN, WeatherCondition.DRIZZLE]:
                components["serenity"] += 0.8 * weight
                components["creativity"] += 0.7 * weight
            elif weather_data["condition"] == WeatherCondition.THUNDERSTORM:
                components["intensity"] += 0.9 * weight
                components["creativity"] += 0.6 * weight
            
            weights_sum += weight
        
        # Blend productivity influence
        if productivity_data:
            weight = self.source_weights["productivity"]
            components["energy"] += productivity_data["energy"] * weight
            components["focus"] += productivity_data["focus"] * weight
            components["intensity"] += productivity_data["intensity"] * weight
            
            weights_sum += weight
        
        # Normalize all components
        for component in components:
            components[component] = min(components[component] / weights_sum, 1.0)
        
        return components
    
    def _determine_primary_atmosphere(self, mood_components: Dict[str, float]) -> AtmosphereType:
        """Determine primary atmosphere based on mood components"""
        
        time_context = self._get_time_context()
        hour = time_context["hour"]
        
        # Time-based atmosphere with mood modifiers
        if 5 <= hour < 9:  # Morning
            if mood_components["serenity"] > 0.7:
                return AtmosphereType.SERENE_MORNING
            else:
                return AtmosphereType.ENERGETIC_NOON
        elif 9 <= hour < 14:  # Late morning / Noon
            if mood_components["energy"] > 0.7:
                return AtmosphereType.ENERGETIC_NOON
            else:
                return AtmosphereType.FOCUSED_AFTERNOON
        elif 14 <= hour < 17:  # Afternoon
            if mood_components["focus"] > 0.7:
                return AtmosphereType.FOCUSED_AFTERNOON
            else:
                return AtmosphereType.CREATIVE_EVENING
        elif 17 <= hour < 21:  # Evening
            if mood_components["creativity"] > 0.6:
                return AtmosphereType.CREATIVE_EVENING
            else:
                return AtmosphereType.CONTEMPLATIVE_NIGHT
        else:  # Night / Late night
            return AtmosphereType.CONTEMPLATIVE_NIGHT
        
        # Override for intense moods
        if mood_components["intensity"] > 0.8:
            return AtmosphereType.STORMY_INTENSITY
    
    def _determine_weather_pattern(
        self, 
        mood_components: Dict[str, float],
        weather_data: Optional[Dict[str, Any]]
    ) -> WeatherPattern:
        """Determine weather pattern for the garden"""
        
        # Special patterns for extreme moods
        if mood_components["intensity"] > 0.9:
            return WeatherPattern.THUNDERSTORM
        elif mood_components["serenity"] > 0.8 and mood_components["energy"] < 0.3:
            return WeatherPattern.MISTY_FOG
        elif (mood_components["energy"] > 0.8 and mood_components["creativity"] > 0.8 and 
              mood_components["focus"] > 0.7):
            return WeatherPattern.AURORA_LIGHTS  # Special coding flow state
        
        # Weather-influenced patterns
        if weather_data:
            condition = weather_data["condition"]
            if condition == WeatherCondition.CLEAR:
                return WeatherPattern.CLEAR_SKIES
            elif condition == WeatherCondition.CLOUDS:
                return WeatherPattern.GENTLE_BREEZE
            elif condition in [WeatherCondition.RAIN, WeatherCondition.DRIZZLE]:
                return WeatherPattern.SOFT_RAIN if mood_components["serenity"] > 0.6 else WeatherPattern.HEAVY_RAIN
            elif condition == WeatherCondition.THUNDERSTORM:
                return WeatherPattern.THUNDERSTORM
            elif condition in [WeatherCondition.FOG, WeatherCondition.MIST]:
                return WeatherPattern.MISTY_FOG
            elif condition == WeatherCondition.SNOW:
                return WeatherPattern.SNOW_FALL
        
        # Default patterns based on mood
        if mood_components["serenity"] > 0.7:
            return WeatherPattern.GENTLE_BREEZE
        elif mood_components["creativity"] > 0.7:
            return WeatherPattern.SOFT_RAIN
        else:
            return WeatherPattern.CLEAR_SKIES
    
    def _generate_visual_properties(
        self, 
        mood_components: Dict[str, float],
        atmosphere: AtmosphereType
    ) -> Dict[str, Any]:
        """Generate visual properties for the mood"""
        
        # Determine dominant color mood
        if mood_components["energy"] > 0.7:
            color_mood = "energetic"
        elif mood_components["focus"] > 0.7:
            color_mood = "focused"
        elif mood_components["creativity"] > 0.7:
            color_mood = "creative"
        elif mood_components["serenity"] > 0.7:
            color_mood = "serene"
        elif mood_components["intensity"] > 0.7:
            color_mood = "intense"
        else:
            color_mood = "contemplative"
        
        colors = self.color_palettes.get(color_mood, self.color_palettes["serene"])
        
        # Lighting style
        if mood_components["energy"] > 0.8:
            lighting = "bright"
        elif mood_components["intensity"] > 0.7:
            lighting = "dramatic"
        elif mood_components["serenity"] > 0.7:
            lighting = "soft"
        elif mood_components["focus"] > 0.7:
            lighting = "focused"
        else:
            lighting = "ambient"
        
        # Particle density
        particles = min(mood_components["energy"] + mood_components["creativity"], 1.0)
        
        # Wind strength
        wind = mood_components["intensity"] * 0.8 + mood_components["energy"] * 0.2
        
        return {
            "colors": colors,
            "lighting": lighting,
            "particles": particles,
            "wind": wind
        }
    
    def _generate_audio_properties(
        self,
        mood_components: Dict[str, float],
        music_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate audio properties for the mood"""
        
        sounds = []
        
        # Base ambient sounds based on mood
        if mood_components["serenity"] > 0.7:
            sounds.extend(["gentle_wind", "bird_songs"])
        if mood_components["intensity"] > 0.6:
            sounds.extend(["strong_wind", "thunder_distant"])
        if mood_components["creativity"] > 0.6:
            sounds.extend(["rain_soft", "water_flow"])
        if mood_components["focus"] > 0.7:
            sounds.extend(["white_noise", "forest_ambiance"])
        
        # Music influence
        music_influence = 0.0
        if music_data:
            music_influence = music_data.get("confidence", 0.5)
            
            # Add music-influenced sounds
            if music_data["primary_mood"] == MoodCategory.ENERGETIC:
                sounds.append("upbeat_nature")
            elif music_data["primary_mood"] == MoodCategory.CALM:
                sounds.append("peaceful_stream")
        
        return {
            "sounds": sounds[:3],  # Limit to 3 concurrent sounds
            "music_influence": music_influence
        }
    
    def _calculate_growth_modifiers(self, mood_components: Dict[str, float]) -> Dict[str, float]:
        """Calculate how mood affects plant growth"""
        
        # Base growth rate from energy and serenity
        base_rate = (mood_components["energy"] * 0.6 + mood_components["serenity"] * 0.4)
        
        # Focus and creativity boost growth
        focus_bonus = mood_components["focus"] * 0.2
        creativity_bonus = mood_components["creativity"] * 0.3
        
        # Intensity can boost or hinder
        if mood_components["intensity"] < 0.7:
            intensity_modifier = mood_components["intensity"] * 0.1
        else:
            intensity_modifier = -0.1  # Too much intensity can stress plants
        
        growth_rate = max(0.5, min(2.0, base_rate + focus_bonus + creativity_bonus + intensity_modifier))
        
        # Bloom probability based on creativity and serenity
        bloom_probability = (mood_components["creativity"] * 0.5 + mood_components["serenity"] * 0.3 + mood_components["energy"] * 0.2)
        
        return {
            "rate": growth_rate,
            "bloom": bloom_probability
        }
    
    def _calculate_synthesis_confidence(self, data_sources: List[str]) -> float:
        """Calculate confidence in the mood synthesis"""
        base_confidence = 0.3  # Minimum confidence from time context
        
        if "spotify" in data_sources:
            base_confidence += 0.3
        if "weather" in data_sources:
            base_confidence += 0.2
        if "wakatime" in data_sources:
            base_confidence += 0.2
        
        return min(base_confidence, 1.0)
    
    def _calculate_transition_timings(self, mood_components: Dict[str, float]) -> Dict[str, float]:
        """Calculate timing for smooth mood transitions"""
        
        # Faster transitions for high energy/intensity
        base_speed = 1.0 - (mood_components["energy"] + mood_components["intensity"]) / 2
        
        return {
            "color_transition": max(0.5, base_speed * 30),      # 0.5-15 seconds
            "lighting_transition": max(1.0, base_speed * 60),   # 1-30 seconds  
            "particle_transition": max(0.3, base_speed * 10),   # 0.3-5 seconds
            "wind_transition": max(2.0, base_speed * 120)       # 2-60 seconds
        }
    
    def _get_default_mood(self) -> MoodSynthesis:
        """Get default mood when synthesis fails"""
        time_context = self._get_time_context()
        
        return MoodSynthesis(
            primary_atmosphere=AtmosphereType.SERENE_MORNING,
            weather_pattern=WeatherPattern.GENTLE_BREEZE,
            energy_level=time_context["energy"],
            focus_level=time_context["focus"],
            creativity_level=0.5,
            serenity_level=time_context["serenity"],
            intensity_level=0.3,
            color_palette=self.color_palettes["serene"],
            lighting_style="ambient",
            particle_density=0.3,
            wind_strength=0.2,
            ambient_sounds=["gentle_wind", "bird_songs"],
            music_influence=0.0,
            growth_rate_modifier=1.0,
            bloom_probability=0.3,
            confidence=0.3,
            data_sources=["time"],
            last_updated=datetime.utcnow(),
            transitions={"color_transition": 10, "lighting_transition": 20, "particle_transition": 5, "wind_transition": 30}
        )
    
    async def _handle_mood_change(self, new_mood: MoodSynthesis):
        """Handle significant mood changes and broadcast events"""
        if not self.current_mood:
            return
        
        # Calculate change magnitude
        energy_change = abs(new_mood.energy_level - self.current_mood.energy_level)
        atmosphere_changed = new_mood.primary_atmosphere != self.current_mood.primary_atmosphere
        weather_changed = new_mood.weather_pattern != self.current_mood.weather_pattern
        
        # Broadcast significant changes
        if energy_change > 0.3 or atmosphere_changed or weather_changed:
            await websocket_manager.broadcast_event(WebSocketEvent(
                type=EventType.ATMOSPHERE_CHANGED,
                data={
                    "old_atmosphere": self.current_mood.primary_atmosphere.value,
                    "new_atmosphere": new_mood.primary_atmosphere.value,
                    "old_weather": self.current_mood.weather_pattern.value,
                    "new_weather": new_mood.weather_pattern.value,
                    "energy_change": energy_change,
                    "confidence": new_mood.confidence,
                    "data_sources": new_mood.data_sources
                },
                timestamp=datetime.utcnow(),
                source="mood_engine"
            ))
    
    async def get_mood_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze mood trends over time"""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            recent_moods = [m for m in self.mood_history if m.last_updated >= cutoff]
            
            if len(recent_moods) < 2:
                return {"error": "Insufficient mood history"}
            
            # Calculate averages
            avg_energy = sum(m.energy_level for m in recent_moods) / len(recent_moods)
            avg_focus = sum(m.focus_level for m in recent_moods) / len(recent_moods)
            avg_creativity = sum(m.creativity_level for m in recent_moods) / len(recent_moods)
            avg_serenity = sum(m.serenity_level for m in recent_moods) / len(recent_moods)
            
            # Most common atmosphere and weather
            atmosphere_counts = {}
            weather_counts = {}
            
            for mood in recent_moods:
                atmosphere_counts[mood.primary_atmosphere.value] = atmosphere_counts.get(mood.primary_atmosphere.value, 0) + 1
                weather_counts[mood.weather_pattern.value] = weather_counts.get(mood.weather_pattern.value, 0) + 1
            
            most_common_atmosphere = max(atmosphere_counts.items(), key=lambda x: x[1])[0]
            most_common_weather = max(weather_counts.items(), key=lambda x: x[1])[0]
            
            # Trend analysis
            first_half = recent_moods[:len(recent_moods)//2]
            second_half = recent_moods[len(recent_moods)//2:]
            
            energy_trend = (sum(m.energy_level for m in second_half) / len(second_half)) - (sum(m.energy_level for m in first_half) / len(first_half))
            
            return {
                "period_hours": hours,
                "moods_analyzed": len(recent_moods),
                "averages": {
                    "energy": avg_energy,
                    "focus": avg_focus,
                    "creativity": avg_creativity,
                    "serenity": avg_serenity
                },
                "most_common": {
                    "atmosphere": most_common_atmosphere,
                    "weather": most_common_weather
                },
                "trends": {
                    "energy": "increasing" if energy_trend > 0.1 else "decreasing" if energy_trend < -0.1 else "stable"
                },
                "data_source_usage": {
                    "spotify": sum(1 for m in recent_moods if "spotify" in m.data_sources) / len(recent_moods),
                    "weather": sum(1 for m in recent_moods if "weather" in m.data_sources) / len(recent_moods),
                    "wakatime": sum(1 for m in recent_moods if "wakatime" in m.data_sources) / len(recent_moods)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze mood trends: {e}")
            return {"error": str(e)}