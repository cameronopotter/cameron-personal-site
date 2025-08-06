"""
Spotify Web API integration service for music data and mood analysis.
"""

import base64
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .base import BaseIntegration, APIResponse, IntegrationError
from .integration_config import integration_settings

import logging
logger = logging.getLogger(__name__)


class MoodCategory(str, Enum):
    """Music mood categories"""
    ENERGETIC = "energetic"
    HAPPY = "happy" 
    CALM = "calm"
    MELANCHOLIC = "melancholic"
    INTENSE = "intense"
    DREAMY = "dreamy"
    FOCUSED = "focused"
    PARTY = "party"


@dataclass
class AudioFeatures:
    """Spotify audio features for a track"""
    track_id: str
    acousticness: float       # 0.0 to 1.0
    danceability: float       # 0.0 to 1.0
    energy: float            # 0.0 to 1.0
    instrumentalness: float  # 0.0 to 1.0
    liveness: float          # 0.0 to 1.0
    loudness: float          # -60 to 0 db
    speechiness: float       # 0.0 to 1.0
    valence: float           # 0.0 to 1.0 (positiveness)
    tempo: float             # BPM
    duration_ms: int
    time_signature: int


@dataclass 
class CurrentlyPlaying:
    """Currently playing track information"""
    track_id: str
    track_name: str
    artist_name: str
    album_name: str
    duration_ms: int
    progress_ms: int
    is_playing: bool
    popularity: int
    explicit: bool
    preview_url: Optional[str]
    external_url: str
    timestamp: datetime
    

@dataclass
class MoodAnalysis:
    """Music mood analysis result"""
    primary_mood: MoodCategory
    mood_scores: Dict[MoodCategory, float]
    energy_level: float      # 0.0 to 1.0
    positivity_level: float  # 0.0 to 1.0
    intensity_level: float   # 0.0 to 1.0
    focus_level: float       # 0.0 to 1.0
    weather_influence: str   # sunny, rainy, stormy, misty, clear
    confidence: float        # 0.0 to 1.0


@dataclass
class ListeningSession:
    """Extended listening session data"""
    start_time: datetime
    end_time: Optional[datetime]
    tracks_played: List[str]
    dominant_mood: MoodCategory
    avg_energy: float
    avg_valence: float
    genre_distribution: Dict[str, int]
    total_duration_ms: int


class SpotifyService(BaseIntegration):
    """Spotify Web API integration service"""
    
    def __init__(self):
        config = integration_settings.spotify
        super().__init__(
            name="spotify",
            base_url=config.base_url,
            timeout=30,
            max_retries=3
        )
        
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.redirect_uri = config.redirect_uri
        self.refresh_token = config.refresh_token
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get Spotify authentication headers"""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}
    
    async def health_check(self) -> bool:
        """Check Spotify API health"""
        try:
            if not await self._ensure_valid_token():
                return False
            
            response = await self.make_request("GET", "/me")
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Spotify health check failed: {e}")
            return False
    
    async def _ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token"""
        if (self.access_token and self.token_expires_at and 
            datetime.utcnow() < self.token_expires_at - timedelta(minutes=5)):
            return True
        
        if self.refresh_token:
            return await self._refresh_access_token()
        
        logger.warning("No valid Spotify token available")
        return False
    
    async def _refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        try:
            # Encode client credentials
            credentials = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }
            
            # Use a separate client for token refresh
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://accounts.spotify.com/api/token",
                    headers=headers,
                    data=data
                )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                
                # Update refresh token if provided
                if "refresh_token" in token_data:
                    self.refresh_token = token_data["refresh_token"]
                
                logger.info("Spotify access token refreshed successfully")
                return True
            
        except Exception as e:
            logger.error(f"Failed to refresh Spotify token: {e}")
        
        return False
    
    async def get_currently_playing(self) -> APIResponse[Optional[CurrentlyPlaying]]:
        """Get currently playing track"""
        try:
            if not await self._ensure_valid_token():
                return APIResponse(
                    success=False,
                    error="No valid Spotify token",
                    service="spotify"
                )
            
            response = await self.make_request("GET", "/me/player/currently-playing")
            
            # No content means nothing is playing
            if response.status_code == 204:
                return APIResponse(
                    success=True,
                    data=None,
                    service="spotify",
                    metadata={"status": "not_playing"}
                )
            
            data = response.json()
            
            if not data or not data.get("item"):
                return APIResponse(
                    success=True,
                    data=None,
                    service="spotify",
                    metadata={"status": "no_track"}
                )
            
            track = data["item"]
            
            current_track = CurrentlyPlaying(
                track_id=track["id"],
                track_name=track["name"],
                artist_name=", ".join(artist["name"] for artist in track["artists"]),
                album_name=track["album"]["name"],
                duration_ms=track["duration_ms"],
                progress_ms=data.get("progress_ms", 0),
                is_playing=data.get("is_playing", False),
                popularity=track.get("popularity", 0),
                explicit=track.get("explicit", False),
                preview_url=track.get("preview_url"),
                external_url=track["external_urls"]["spotify"],
                timestamp=datetime.utcnow()
            )
            
            return APIResponse(
                success=True,
                data=current_track,
                service="spotify",
                metadata={
                    "device": data.get("device", {}).get("name", "unknown"),
                    "context": data.get("context", {}).get("type", "unknown")
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get currently playing: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="spotify"
            )
    
    async def get_audio_features(self, track_id: str) -> APIResponse[AudioFeatures]:
        """Get audio features for a track"""
        try:
            if not await self._ensure_valid_token():
                return APIResponse(
                    success=False,
                    error="No valid Spotify token",
                    service="spotify"
                )
            
            response = await self.make_request("GET", f"/audio-features/{track_id}")
            data = response.json()
            
            features = AudioFeatures(
                track_id=data["id"],
                acousticness=data["acousticness"],
                danceability=data["danceability"],
                energy=data["energy"],
                instrumentalness=data["instrumentalness"],
                liveness=data["liveness"],
                loudness=data["loudness"],
                speechiness=data["speechiness"],
                valence=data["valence"],
                tempo=data["tempo"],
                duration_ms=data["duration_ms"],
                time_signature=data["time_signature"]
            )
            
            return APIResponse(
                success=True,
                data=features,
                service="spotify",
                metadata={"track_id": track_id}
            )
            
        except Exception as e:
            logger.error(f"Failed to get audio features for {track_id}: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="spotify"
            )
    
    async def get_recently_played(self, limit: int = 50) -> APIResponse[List[Dict[str, Any]]]:
        """Get recently played tracks"""
        try:
            if not await self._ensure_valid_token():
                return APIResponse(
                    success=False,
                    error="No valid Spotify token",
                    service="spotify"
                )
            
            params = {"limit": min(limit, 50)}
            response = await self.make_request("GET", "/me/player/recently-played", params=params)
            data = response.json()
            
            tracks = []
            for item in data.get("items", []):
                track = item["track"]
                played_at = datetime.fromisoformat(item["played_at"].replace("Z", "+00:00"))
                
                tracks.append({
                    "track_id": track["id"],
                    "track_name": track["name"],
                    "artist_name": ", ".join(artist["name"] for artist in track["artists"]),
                    "album_name": track["album"]["name"],
                    "played_at": played_at,
                    "duration_ms": track["duration_ms"],
                    "popularity": track.get("popularity", 0)
                })
            
            return APIResponse(
                success=True,
                data=tracks,
                service="spotify",
                metadata={"tracks_returned": len(tracks)}
            )
            
        except Exception as e:
            logger.error(f"Failed to get recently played tracks: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="spotify"
            )
    
    async def analyze_current_mood(self) -> APIResponse[Optional[MoodAnalysis]]:
        """Analyze current music mood"""
        try:
            # Get currently playing track
            current_response = await self.get_currently_playing()
            if not current_response.success or not current_response.data:
                return APIResponse(
                    success=True,
                    data=None,
                    service="spotify",
                    metadata={"status": "no_music_playing"}
                )
            
            current_track = current_response.data
            
            # Get audio features
            features_response = await self.get_audio_features(current_track.track_id)
            if not features_response.success:
                return APIResponse(
                    success=False,
                    error="Failed to get audio features",
                    service="spotify"
                )
            
            features = features_response.data
            
            # Calculate mood scores
            mood_scores = self._calculate_mood_scores(features)
            primary_mood = max(mood_scores.items(), key=lambda x: x[1])[0]
            
            # Calculate additional metrics
            energy_level = features.energy
            positivity_level = features.valence
            intensity_level = (features.energy + (features.loudness + 60) / 60) / 2
            focus_level = 1.0 - features.danceability * features.valence
            
            # Map to weather influence
            weather_influence = self._map_mood_to_weather(features)
            
            # Calculate confidence based on how distinct the primary mood is
            sorted_scores = sorted(mood_scores.values(), reverse=True)
            confidence = (sorted_scores[0] - sorted_scores[1]) if len(sorted_scores) > 1 else 1.0
            
            mood_analysis = MoodAnalysis(
                primary_mood=primary_mood,
                mood_scores=mood_scores,
                energy_level=energy_level,
                positivity_level=positivity_level,
                intensity_level=intensity_level,
                focus_level=focus_level,
                weather_influence=weather_influence,
                confidence=confidence
            )
            
            return APIResponse(
                success=True,
                data=mood_analysis,
                service="spotify",
                metadata={
                    "track_name": current_track.track_name,
                    "artist_name": current_track.artist_name
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze current mood: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="spotify"
            )
    
    def _calculate_mood_scores(self, features: AudioFeatures) -> Dict[MoodCategory, float]:
        """Calculate mood scores based on audio features"""
        scores = {}
        
        # Energetic: high energy, high tempo
        scores[MoodCategory.ENERGETIC] = (
            features.energy * 0.4 +
            min(features.tempo / 180, 1.0) * 0.3 +
            features.danceability * 0.3
        )
        
        # Happy: high valence, moderate energy
        scores[MoodCategory.HAPPY] = (
            features.valence * 0.5 +
            features.energy * 0.3 +
            features.danceability * 0.2
        )
        
        # Calm: low energy, high acousticness
        scores[MoodCategory.CALM] = (
            (1.0 - features.energy) * 0.4 +
            features.acousticness * 0.3 +
            (1.0 - features.loudness / -60) * 0.3
        )
        
        # Melancholic: low valence, moderate acousticness
        scores[MoodCategory.MELANCHOLIC] = (
            (1.0 - features.valence) * 0.5 +
            features.acousticness * 0.2 +
            (1.0 - features.energy) * 0.3
        )
        
        # Intense: high energy, high loudness
        scores[MoodCategory.INTENSE] = (
            features.energy * 0.4 +
            (features.loudness + 60) / 60 * 0.4 +
            (1.0 - features.acousticness) * 0.2
        )
        
        # Dreamy: high acousticness, low energy, moderate valence
        scores[MoodCategory.DREAMY] = (
            features.acousticness * 0.4 +
            (1.0 - features.energy) * 0.3 +
            abs(features.valence - 0.5) * 0.3  # Neutral valence
        )
        
        # Focused: low danceability, moderate energy, low valence variation
        scores[MoodCategory.FOCUSED] = (
            (1.0 - features.danceability) * 0.4 +
            abs(features.energy - 0.5) * 0.3 +  # Moderate energy
            features.instrumentalness * 0.3
        )
        
        # Party: high danceability, high energy, high valence
        scores[MoodCategory.PARTY] = (
            features.danceability * 0.4 +
            features.energy * 0.3 +
            features.valence * 0.3
        )
        
        return scores
    
    def _map_mood_to_weather(self, features: AudioFeatures) -> str:
        """Map audio features to weather conditions"""
        if features.energy > 0.7 and features.valence > 0.6:
            return "sunny"
        elif features.energy < 0.3 and features.valence < 0.4:
            return "rainy"
        elif features.energy > 0.8 and features.loudness > -5:
            return "stormy"
        elif features.acousticness > 0.6 and features.energy < 0.5:
            return "misty"
        else:
            return "clear"
    
    async def get_listening_trends(self, days: int = 7) -> Dict[str, Any]:
        """Analyze listening trends over time"""
        try:
            # Get recently played tracks
            recent_response = await self.get_recently_played(50)
            if not recent_response.success:
                return {}
            
            tracks = recent_response.data
            
            # Filter by time period
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            filtered_tracks = [
                t for t in tracks 
                if t["played_at"] >= cutoff_time
            ]
            
            if not filtered_tracks:
                return {"period": f"{days} days", "tracks_analyzed": 0}
            
            # Analyze trends
            total_duration = sum(t["duration_ms"] for t in filtered_tracks)
            avg_popularity = sum(t["popularity"] for t in filtered_tracks) / len(filtered_tracks)
            
            # Group by day
            daily_counts = {}
            for track in filtered_tracks:
                day = track["played_at"].date().isoformat()
                daily_counts[day] = daily_counts.get(day, 0) + 1
            
            return {
                "period": f"{days} days",
                "tracks_analyzed": len(filtered_tracks),
                "total_listening_time_hours": total_duration / (1000 * 60 * 60),
                "avg_track_popularity": avg_popularity,
                "daily_listening_counts": daily_counts,
                "most_active_day": max(daily_counts.items(), key=lambda x: x[1])[0] if daily_counts else None
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze listening trends: {e}")
            return {}