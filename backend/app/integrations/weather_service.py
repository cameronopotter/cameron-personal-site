"""
Weather API integration service for environmental data and garden atmosphere.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .base import BaseIntegration, APIResponse
from .integration_config import integration_settings

import logging
logger = logging.getLogger(__name__)


class WeatherCondition(str, Enum):
    """Weather condition categories"""
    CLEAR = "clear"
    CLOUDS = "clouds"
    RAIN = "rain"
    DRIZZLE = "drizzle"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    MIST = "mist"
    SMOKE = "smoke"
    HAZE = "haze"
    DUST = "dust"
    FOG = "fog"
    SAND = "sand"
    ASH = "ash"
    SQUALL = "squall"
    TORNADO = "tornado"


@dataclass
class CurrentWeather:
    """Current weather data"""
    location: str
    condition: WeatherCondition
    description: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    visibility: Optional[int]
    wind_speed: float
    wind_direction: int
    clouds: int
    uv_index: Optional[float]
    sunrise: datetime
    sunset: datetime
    timestamp: datetime


@dataclass
class WeatherForecast:
    """Weather forecast data"""
    date: datetime
    condition: WeatherCondition
    description: str
    temp_min: float
    temp_max: float
    humidity: int
    wind_speed: float
    clouds: int
    precipitation_chance: int


@dataclass
class SeasonalInfluence:
    """Seasonal influence on garden atmosphere"""
    season: str
    day_length_hours: float
    solar_angle: float
    typical_temperature: float
    growth_factor: float  # 0.0 to 1.0
    color_temperature: int  # Kelvin
    atmospheric_density: float  # 0.0 to 1.0


@dataclass
class AtmosphericMood:
    """Weather-based atmospheric mood"""
    primary_mood: str
    intensity: float  # 0.0 to 1.0
    color_palette: List[str]  # Hex colors
    lighting_style: str
    particle_effects: List[str]
    sound_ambiance: str
    growth_modifier: float  # 0.5 to 1.5


class WeatherService(BaseIntegration):
    """Weather API integration service using OpenWeatherMap"""
    
    def __init__(self):
        config = integration_settings.weather
        super().__init__(
            name="weather",
            base_url=config.base_url,
            api_key=config.api_key,
            timeout=15,
            max_retries=3
        )
        
        self.default_location = config.default_location
        self.units = config.units
        self.include_forecast = config.include_forecast
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get weather API authentication headers"""
        return {}  # OpenWeatherMap uses API key in query params
    
    async def health_check(self) -> bool:
        """Check weather API health"""
        try:
            params = {
                "q": self.default_location,
                "appid": self.api_key,
                "units": self.units
            }
            response = await self.make_request("GET", "/weather", params=params)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Weather health check failed: {e}")
            return False
    
    async def get_current_weather(self, location: Optional[str] = None) -> APIResponse[CurrentWeather]:
        """Get current weather data"""
        try:
            location = location or self.default_location
            
            params = {
                "q": location,
                "appid": self.api_key,
                "units": self.units
            }
            
            response = await self.make_request("GET", "/weather", params=params)
            data = response.json()
            
            # Parse weather condition
            condition_code = data["weather"][0]["main"].lower()
            condition = WeatherCondition(condition_code) if condition_code in [c.value for c in WeatherCondition] else WeatherCondition.CLEAR
            
            current_weather = CurrentWeather(
                location=data["name"],
                condition=condition,
                description=data["weather"][0]["description"],
                temperature=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                humidity=data["main"]["humidity"],
                pressure=data["main"]["pressure"],
                visibility=data.get("visibility"),
                wind_speed=data.get("wind", {}).get("speed", 0),
                wind_direction=data.get("wind", {}).get("deg", 0),
                clouds=data["clouds"]["all"],
                uv_index=None,  # Need separate API call
                sunrise=datetime.fromtimestamp(data["sys"]["sunrise"]),
                sunset=datetime.fromtimestamp(data["sys"]["sunset"]),
                timestamp=datetime.utcnow()
            )
            
            return APIResponse(
                success=True,
                data=current_weather,
                service="weather",
                metadata={
                    "location": location,
                    "country": data["sys"]["country"]
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get current weather: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="weather"
            )
    
    async def get_weather_forecast(self, location: Optional[str] = None, days: int = 5) -> APIResponse[List[WeatherForecast]]:
        """Get weather forecast"""
        try:
            location = location or self.default_location
            
            params = {
                "q": location,
                "appid": self.api_key,
                "units": self.units,
                "cnt": min(days * 8, 40)  # 3-hour intervals, max 5 days
            }
            
            response = await self.make_request("GET", "/forecast", params=params)
            data = response.json()
            
            forecasts = []
            daily_forecasts = {}
            
            # Group by day and take daily summary
            for item in data["list"]:
                dt = datetime.fromtimestamp(item["dt"])
                date_key = dt.date()
                
                if date_key not in daily_forecasts:
                    condition_code = item["weather"][0]["main"].lower()
                    condition = WeatherCondition(condition_code) if condition_code in [c.value for c in WeatherCondition] else WeatherCondition.CLEAR
                    
                    daily_forecasts[date_key] = WeatherForecast(
                        date=dt.replace(hour=12, minute=0, second=0),
                        condition=condition,
                        description=item["weather"][0]["description"],
                        temp_min=item["main"]["temp_min"],
                        temp_max=item["main"]["temp_max"],
                        humidity=item["main"]["humidity"],
                        wind_speed=item.get("wind", {}).get("speed", 0),
                        clouds=item["clouds"]["all"],
                        precipitation_chance=int(item.get("pop", 0) * 100)
                    )
                else:
                    # Update min/max temperatures
                    forecast = daily_forecasts[date_key]
                    forecast.temp_min = min(forecast.temp_min, item["main"]["temp_min"])
                    forecast.temp_max = max(forecast.temp_max, item["main"]["temp_max"])
            
            forecasts = list(daily_forecasts.values())
            forecasts.sort(key=lambda f: f.date)
            
            return APIResponse(
                success=True,
                data=forecasts[:days],
                service="weather",
                metadata={
                    "location": location,
                    "days_requested": days,
                    "forecasts_returned": len(forecasts[:days])
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get weather forecast: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="weather"
            )
    
    async def get_uv_index(self, lat: float, lon: float) -> APIResponse[float]:
        """Get UV index for coordinates"""
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key
            }
            
            response = await self.make_request("GET", "/uvi", params=params)
            data = response.json()
            
            uv_index = data.get("value", 0.0)
            
            return APIResponse(
                success=True,
                data=uv_index,
                service="weather",
                metadata={"coordinates": f"{lat},{lon}"}
            )
            
        except Exception as e:
            logger.error(f"Failed to get UV index: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="weather"
            )
    
    def calculate_seasonal_influence(self, location_lat: float = 51.5074) -> SeasonalInfluence:
        """Calculate seasonal influence based on date and location"""
        now = datetime.utcnow()
        day_of_year = now.timetuple().tm_yday
        
        # Calculate season
        if day_of_year < 80 or day_of_year > 355:
            season = "winter"
        elif day_of_year < 172:
            season = "spring"
        elif day_of_year < 266:
            season = "summer"
        else:
            season = "autumn"
        
        # Calculate solar angle (simplified)
        solar_declination = 23.45 * (3.14159 / 180) * \
                           (1.0 - (day_of_year - 81) / 365.0 * 2 * 3.14159)
        solar_angle = 90 - abs(location_lat - solar_declination * (180 / 3.14159))
        
        # Calculate day length (simplified)
        latitude_rad = location_lat * (3.14159 / 180)
        declination_rad = solar_declination
        
        hour_angle = (-1 * (location_lat * (3.14159 / 180)) * 
                     (solar_declination * (3.14159 / 180)))
        day_length = 12 + (24 / 3.14159) * hour_angle
        day_length = max(8, min(16, day_length))  # Clamp between 8-16 hours
        
        # Seasonal factors
        seasonal_factors = {
            "spring": {"growth": 0.8, "temp": 15, "color": 5500},
            "summer": {"growth": 1.0, "temp": 25, "color": 6500},
            "autumn": {"growth": 0.6, "temp": 12, "color": 3000},
            "winter": {"growth": 0.3, "temp": 3, "color": 2700}
        }
        
        factors = seasonal_factors[season]
        
        return SeasonalInfluence(
            season=season,
            day_length_hours=day_length,
            solar_angle=solar_angle,
            typical_temperature=factors["temp"],
            growth_factor=factors["growth"],
            color_temperature=factors["color"],
            atmospheric_density=1.0 - (solar_angle / 90.0)
        )
    
    def analyze_atmospheric_mood(self, weather: CurrentWeather) -> AtmosphericMood:
        """Analyze weather conditions to determine atmospheric mood"""
        
        # Define mood mappings
        mood_mappings = {
            WeatherCondition.CLEAR: {
                "mood": "bright",
                "intensity": 0.8,
                "colors": ["#87CEEB", "#FFD700", "#98FB98"],
                "lighting": "bright",
                "particles": ["sunbeams", "dust_motes"],
                "ambiance": "peaceful"
            },
            WeatherCondition.CLOUDS: {
                "mood": "contemplative", 
                "intensity": 0.5,
                "colors": ["#708090", "#B0C4DE", "#F5F5DC"],
                "lighting": "diffused",
                "particles": ["clouds"],
                "ambiance": "serene"
            },
            WeatherCondition.RAIN: {
                "mood": "melancholic",
                "intensity": 0.7,
                "colors": ["#2F4F4F", "#4682B4", "#778899"],
                "lighting": "dim",
                "particles": ["raindrops", "ripples"],
                "ambiance": "rain"
            },
            WeatherCondition.THUNDERSTORM: {
                "mood": "dramatic",
                "intensity": 1.0,
                "colors": ["#1C1C1C", "#4B0082", "#FF6347"],
                "lighting": "flickering",
                "particles": ["lightning", "heavy_rain"],
                "ambiance": "thunder"
            },
            WeatherCondition.SNOW: {
                "mood": "serene",
                "intensity": 0.6,
                "colors": ["#F0F8FF", "#E6E6FA", "#B0E0E6"],
                "lighting": "soft",
                "particles": ["snowflakes"],
                "ambiance": "winter_wind"
            },
            WeatherCondition.FOG: {
                "mood": "mysterious",
                "intensity": 0.4,
                "colors": ["#696969", "#D3D3D3", "#F5F5F5"],
                "lighting": "muted",
                "particles": ["fog", "mist"],
                "ambiance": "mysterious"
            }
        }
        
        # Get base mood
        mood_data = mood_mappings.get(weather.condition, mood_mappings[WeatherCondition.CLEAR])
        
        # Adjust intensity based on weather parameters
        intensity_modifiers = 0
        if weather.wind_speed > 20:
            intensity_modifiers += 0.2
        if weather.temperature < 0:
            intensity_modifiers += 0.1
        if weather.humidity > 80:
            intensity_modifiers += 0.1
        if weather.pressure < 1000:
            intensity_modifiers += 0.1
        
        adjusted_intensity = min(1.0, mood_data["intensity"] + intensity_modifiers)
        
        # Calculate growth modifier based on conditions
        growth_modifier = 1.0
        if weather.condition == WeatherCondition.RAIN:
            growth_modifier = 1.2  # Rain helps growth
        elif weather.condition == WeatherCondition.CLEAR:
            growth_modifier = 1.1  # Sun helps growth
        elif weather.condition in [WeatherCondition.SNOW, WeatherCondition.FOG]:
            growth_modifier = 0.8  # Harsh conditions slow growth
        elif weather.condition == WeatherCondition.THUNDERSTORM:
            growth_modifier = 0.9  # Drama but some growth
        
        # Adjust for temperature
        if weather.temperature < 5:
            growth_modifier *= 0.7
        elif weather.temperature > 30:
            growth_modifier *= 0.8
        elif 15 <= weather.temperature <= 25:
            growth_modifier *= 1.1  # Optimal growing temperature
        
        return AtmosphericMood(
            primary_mood=mood_data["mood"],
            intensity=adjusted_intensity,
            color_palette=mood_data["colors"],
            lighting_style=mood_data["lighting"],
            particle_effects=mood_data["particles"],
            sound_ambiance=mood_data["ambiance"],
            growth_modifier=growth_modifier
        )
    
    async def get_location_coordinates(self, location: str) -> APIResponse[Dict[str, float]]:
        """Get coordinates for a location using geocoding"""
        try:
            params = {
                "q": location,
                "appid": self.api_key,
                "limit": 1
            }
            
            response = await self.make_request("GET", "/geocoding/v1/direct", params=params)
            data = response.json()
            
            if not data:
                return APIResponse(
                    success=False,
                    error=f"Location '{location}' not found",
                    service="weather"
                )
            
            location_data = data[0]
            coordinates = {
                "lat": location_data["lat"],
                "lon": location_data["lon"]
            }
            
            return APIResponse(
                success=True,
                data=coordinates,
                service="weather",
                metadata={
                    "location": location,
                    "full_name": f"{location_data.get('name', '')}, {location_data.get('country', '')}"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get coordinates for {location}: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="weather"
            )
    
    async def get_comprehensive_weather_data(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive weather data including mood analysis"""
        try:
            location = location or self.default_location
            
            # Get current weather
            current_response = await self.get_current_weather(location)
            if not current_response.success:
                return {"error": current_response.error}
            
            current_weather = current_response.data
            
            # Get forecast
            forecast_data = []
            if self.include_forecast:
                forecast_response = await self.get_weather_forecast(location, 5)
                if forecast_response.success:
                    forecast_data = forecast_response.data
            
            # Calculate seasonal influence
            coords_response = await self.get_location_coordinates(location)
            seasonal_influence = self.calculate_seasonal_influence(
                coords_response.data["lat"] if coords_response.success else 51.5074
            )
            
            # Analyze atmospheric mood
            atmospheric_mood = self.analyze_atmospheric_mood(current_weather)
            
            return {
                "current": {
                    "condition": current_weather.condition.value,
                    "description": current_weather.description,
                    "temperature": current_weather.temperature,
                    "feels_like": current_weather.feels_like,
                    "humidity": current_weather.humidity,
                    "wind_speed": current_weather.wind_speed,
                    "clouds": current_weather.clouds,
                    "timestamp": current_weather.timestamp.isoformat()
                },
                "forecast": [
                    {
                        "date": f.date.isoformat(),
                        "condition": f.condition.value,
                        "temp_min": f.temp_min,
                        "temp_max": f.temp_max,
                        "precipitation_chance": f.precipitation_chance
                    } for f in forecast_data
                ],
                "seasonal": {
                    "season": seasonal_influence.season,
                    "day_length_hours": seasonal_influence.day_length_hours,
                    "growth_factor": seasonal_influence.growth_factor,
                    "color_temperature": seasonal_influence.color_temperature
                },
                "atmosphere": {
                    "mood": atmospheric_mood.primary_mood,
                    "intensity": atmospheric_mood.intensity,
                    "colors": atmospheric_mood.color_palette,
                    "lighting": atmospheric_mood.lighting_style,
                    "effects": atmospheric_mood.particle_effects,
                    "growth_modifier": atmospheric_mood.growth_modifier
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive weather data: {e}")
            return {"error": str(e)}