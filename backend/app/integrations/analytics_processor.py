"""
Analytics processing engine for visitor journey analysis and engagement insights.
"""

import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

from .websocket_manager import websocket_manager, WebSocketEvent, EventType, ConnectionRole
from .integration_config import integration_settings

import logging
logger = logging.getLogger(__name__)


class InteractionType(str, Enum):
    """Types of visitor interactions"""
    PAGE_VIEW = "page_view"
    PLANT_HOVER = "plant_hover"
    PLANT_CLICK = "plant_click"
    CONSTELLATION_VIEW = "constellation_view"
    PROJECT_MODAL_OPEN = "project_modal_open"
    SKILL_INTERACTION = "skill_interaction"
    SETTINGS_CHANGE = "settings_change"
    GARDEN_NAVIGATION = "garden_navigation"
    WEATHER_INTERACTION = "weather_interaction"
    PERFORMANCE_FEEDBACK = "performance_feedback"


class EngagementLevel(str, Enum):
    """Visitor engagement levels"""
    PASSIVE = "passive"           # Just viewing
    CURIOUS = "curious"          # Some interactions
    ENGAGED = "engaged"          # Multiple interactions
    HIGHLY_ENGAGED = "highly_engaged"  # Deep exploration
    POWER_USER = "power_user"    # Advanced usage


@dataclass
class VisitorProfile:
    """Anonymous visitor profile"""
    visitor_id: str               # Hashed identifier
    first_visit: datetime
    last_visit: datetime
    total_visits: int
    total_session_time: int       # seconds
    avg_session_time: float       # seconds
    engagement_level: EngagementLevel
    favorite_projects: List[str]  # Most interacted with
    preferred_times: List[int]    # Hours of day (0-23)
    device_info: Dict[str, Any]   # Browser, OS, screen size
    geographic_region: Optional[str]  # Country/region if available
    interaction_patterns: Dict[InteractionType, int]
    journey_segments: List[str]   # Journey through the garden
    conversion_events: List[str]  # Achieved goals (contact, hiring interest, etc.)


@dataclass
class InteractionEvent:
    """Individual interaction event"""
    event_id: str
    visitor_id: str
    interaction_type: InteractionType
    timestamp: datetime
    metadata: Dict[str, Any]      # Context-specific data
    session_id: str
    page_url: str
    referrer: Optional[str]
    user_agent: str
    screen_resolution: Optional[str]
    duration: Optional[int]       # For timed interactions


@dataclass 
class SessionAnalysis:
    """Analysis of a visitor session"""
    session_id: str
    visitor_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: int
    page_views: int
    interactions: int
    bounce_rate: float            # 0.0 to 1.0
    engagement_score: float       # 0.0 to 1.0
    journey_path: List[str]       # Sequence of interactions
    conversion_achieved: bool
    device_type: str              # desktop, mobile, tablet
    exit_point: str              # Where user left


@dataclass
class EngagementMetrics:
    """Comprehensive engagement metrics"""
    total_visitors: int
    unique_visitors_24h: int
    avg_session_duration: float
    bounce_rate: float
    pages_per_session: float
    conversion_rate: float
    engagement_distribution: Dict[EngagementLevel, int]
    popular_content: List[Dict[str, Any]]
    traffic_sources: Dict[str, int]
    device_breakdown: Dict[str, int]
    geographic_distribution: Dict[str, int]
    peak_hours: List[int]
    retention_metrics: Dict[str, float]


class AnalyticsProcessor:
    """Analytics processing and visitor intelligence engine"""
    
    def __init__(self):
        self.visitor_profiles: Dict[str, VisitorProfile] = {}
        self.interaction_events: List[InteractionEvent] = []
        self.active_sessions: Dict[str, SessionAnalysis] = {}
        self.privacy_config = integration_settings.privacy
        
        # Analytics thresholds
        self.engagement_thresholds = {
            EngagementLevel.PASSIVE: {"interactions": 0, "time": 0},
            EngagementLevel.CURIOUS: {"interactions": 3, "time": 30},
            EngagementLevel.ENGAGED: {"interactions": 10, "time": 120},
            EngagementLevel.HIGHLY_ENGAGED: {"interactions": 25, "time": 300},
            EngagementLevel.POWER_USER: {"interactions": 50, "time": 600}
        }
        
        # Journey segments
        self.journey_segments = {
            "arrival": ["page_view"],
            "discovery": ["plant_hover", "constellation_view"],
            "exploration": ["plant_click", "project_modal_open"],
            "deep_dive": ["skill_interaction", "settings_change"],
            "engagement": ["multiple_project_views", "long_session"],
            "conversion": ["contact_attempt", "hiring_interest"]
        }
    
    def _anonymize_visitor_id(self, raw_identifier: str) -> str:
        """Create anonymous but consistent visitor ID"""
        if not self.privacy_config.hash_ip_addresses:
            return raw_identifier
        
        # Hash the identifier for privacy
        return hashlib.sha256(raw_identifier.encode()).hexdigest()[:16]
    
    def _anonymize_user_agent(self, user_agent: str) -> str:
        """Anonymize user agent while preserving useful info"""
        if not self.privacy_config.hash_user_agents:
            return user_agent
        
        # Extract only browser and OS info, remove version details
        import re
        
        browser_patterns = {
            'chrome': r'Chrome/[\d.]+',
            'firefox': r'Firefox/[\d.]+', 
            'safari': r'Safari/[\d.]+',
            'edge': r'Edge/[\d.]+'
        }
        
        os_patterns = {
            'windows': r'Windows NT [\d.]+',
            'macos': r'Mac OS X [\d_]+',
            'linux': r'Linux',
            'android': r'Android [\d.]+',
            'ios': r'iPhone OS [\d_]+'
        }
        
        browser = "unknown"
        os = "unknown"
        
        user_agent_lower = user_agent.lower()
        
        for name, pattern in browser_patterns.items():
            if name in user_agent_lower:
                browser = name
                break
        
        for name, pattern in os_patterns.items():
            if name.replace('_', ' ') in user_agent_lower.replace('_', ' '):
                os = name
                break
        
        return f"{browser}/{os}"
    
    async def track_interaction(
        self,
        raw_visitor_id: str,
        interaction_type: InteractionType,
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        page_url: str = "/",
        referrer: Optional[str] = None,
        user_agent: str = "",
        screen_resolution: Optional[str] = None,
        duration: Optional[int] = None
    ) -> str:
        """Track a visitor interaction event"""
        
        try:
            # Anonymize visitor ID
            visitor_id = self._anonymize_visitor_id(raw_visitor_id)
            
            # Generate event ID
            event_id = str(uuid.uuid4())
            
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Anonymize user agent
            anonymized_user_agent = self._anonymize_user_agent(user_agent)
            
            # Create interaction event
            interaction_event = InteractionEvent(
                event_id=event_id,
                visitor_id=visitor_id,
                interaction_type=interaction_type,
                timestamp=datetime.utcnow(),
                metadata=metadata or {},
                session_id=session_id,
                page_url=page_url,
                referrer=referrer,
                user_agent=anonymized_user_agent,
                screen_resolution=screen_resolution,
                duration=duration
            )
            
            # Store event
            self.interaction_events.append(interaction_event)
            
            # Limit event storage (keep last 10000 events)
            if len(self.interaction_events) > 10000:
                self.interaction_events = self.interaction_events[-10000:]
            
            # Update visitor profile
            await self._update_visitor_profile(interaction_event)
            
            # Update session analysis
            await self._update_session_analysis(interaction_event)
            
            # Check for significant events
            await self._check_analytics_events(interaction_event)
            
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to track interaction: {e}")
            return ""
    
    async def _update_visitor_profile(self, event: InteractionEvent):
        """Update visitor profile with new interaction"""
        
        visitor_id = event.visitor_id
        
        # Get or create visitor profile
        if visitor_id not in self.visitor_profiles:
            self.visitor_profiles[visitor_id] = VisitorProfile(
                visitor_id=visitor_id,
                first_visit=event.timestamp,
                last_visit=event.timestamp,
                total_visits=1,
                total_session_time=0,
                avg_session_time=0,
                engagement_level=EngagementLevel.PASSIVE,
                favorite_projects=[],
                preferred_times=[],
                device_info=self._parse_device_info(event.user_agent, event.screen_resolution),
                geographic_region=None,
                interaction_patterns={},
                journey_segments=[],
                conversion_events=[]
            )
        
        profile = self.visitor_profiles[visitor_id]
        
        # Update basic info
        profile.last_visit = event.timestamp
        
        # Update interaction patterns
        if event.interaction_type not in profile.interaction_patterns:
            profile.interaction_patterns[event.interaction_type] = 0
        profile.interaction_patterns[event.interaction_type] += 1
        
        # Update preferred times
        hour = event.timestamp.hour
        if hour not in profile.preferred_times:
            profile.preferred_times.append(hour)
        
        # Update favorite projects
        if (event.interaction_type in [InteractionType.PLANT_CLICK, InteractionType.PROJECT_MODAL_OPEN] and
            "project_name" in event.metadata):
            project_name = event.metadata["project_name"]
            if project_name not in profile.favorite_projects:
                profile.favorite_projects.append(project_name)
            # Keep only top 5 favorite projects
            profile.favorite_projects = profile.favorite_projects[-5:]
        
        # Update journey segments
        segment = self._determine_journey_segment(event.interaction_type)
        if segment and (not profile.journey_segments or profile.journey_segments[-1] != segment):
            profile.journey_segments.append(segment)
        
        # Update conversion events
        if self._is_conversion_event(event):
            conversion_type = event.metadata.get("conversion_type", "unknown")
            if conversion_type not in profile.conversion_events:
                profile.conversion_events.append(conversion_type)
        
        # Recalculate engagement level
        profile.engagement_level = self._calculate_engagement_level(profile)
    
    async def _update_session_analysis(self, event: InteractionEvent):
        """Update session analysis with new event"""
        
        session_id = event.session_id
        
        # Get or create session analysis
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = SessionAnalysis(
                session_id=session_id,
                visitor_id=event.visitor_id,
                start_time=event.timestamp,
                end_time=None,
                duration_seconds=0,
                page_views=0,
                interactions=0,
                bounce_rate=1.0,
                engagement_score=0.0,
                journey_path=[],
                conversion_achieved=False,
                device_type=self._determine_device_type(event.user_agent),
                exit_point=""
            )
        
        session = self.active_sessions[session_id]
        
        # Update session metrics
        session.end_time = event.timestamp
        session.duration_seconds = int((session.end_time - session.start_time).total_seconds())
        session.interactions += 1
        
        if event.interaction_type == InteractionType.PAGE_VIEW:
            session.page_views += 1
        
        # Update journey path
        interaction_name = event.interaction_type.value
        if event.metadata.get("project_name"):
            interaction_name += f":{event.metadata['project_name']}"
        session.journey_path.append(interaction_name)
        
        # Calculate bounce rate (if more than 1 interaction or > 30 seconds, not a bounce)
        if session.interactions > 1 or session.duration_seconds > 30:
            session.bounce_rate = 0.0
        
        # Calculate engagement score
        session.engagement_score = self._calculate_session_engagement_score(session)
        
        # Check for conversions
        if self._is_conversion_event(event):
            session.conversion_achieved = True
        
        # Clean up old sessions (remove sessions older than 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.active_sessions = {
            sid: sess for sid, sess in self.active_sessions.items()
            if sess.start_time >= cutoff or sess.end_time is None or sess.end_time >= cutoff
        }
    
    def _parse_device_info(self, user_agent: str, screen_resolution: Optional[str]) -> Dict[str, Any]:
        """Parse device information from user agent and screen resolution"""
        
        device_info = {
            "browser": "unknown",
            "os": "unknown", 
            "device_type": "unknown",
            "screen_width": None,
            "screen_height": None
        }
        
        if user_agent:
            # Extract browser and OS (already anonymized)
            parts = user_agent.split('/')
            if len(parts) >= 2:
                device_info["browser"] = parts[0]
                device_info["os"] = parts[1]
        
        # Parse screen resolution
        if screen_resolution:
            try:
                width, height = screen_resolution.split('x')
                device_info["screen_width"] = int(width)
                device_info["screen_height"] = int(height)
            except:
                pass
        
        # Determine device type
        device_info["device_type"] = self._determine_device_type(user_agent)
        
        return device_info
    
    def _determine_device_type(self, user_agent: str) -> str:
        """Determine device type from user agent"""
        user_agent_lower = user_agent.lower()
        
        if any(mobile in user_agent_lower for mobile in ['mobile', 'android', 'iphone']):
            return "mobile"
        elif any(tablet in user_agent_lower for tablet in ['tablet', 'ipad']):
            return "tablet"
        else:
            return "desktop"
    
    def _determine_journey_segment(self, interaction_type: InteractionType) -> Optional[str]:
        """Determine which journey segment an interaction belongs to"""
        for segment, interactions in self.journey_segments.items():
            if interaction_type.value in interactions:
                return segment
        return None
    
    def _is_conversion_event(self, event: InteractionEvent) -> bool:
        """Check if an event represents a conversion"""
        conversion_indicators = [
            "contact_form_submit",
            "hiring_interest_click",
            "resume_download",
            "project_external_link_click"
        ]
        
        return (event.metadata.get("conversion_type") in conversion_indicators or
                event.metadata.get("is_conversion", False))
    
    def _calculate_engagement_level(self, profile: VisitorProfile) -> EngagementLevel:
        """Calculate visitor engagement level"""
        
        total_interactions = sum(profile.interaction_patterns.values())
        
        # Find the highest engagement level the visitor qualifies for
        for level in reversed(list(EngagementLevel)):
            threshold = self.engagement_thresholds[level]
            if (total_interactions >= threshold["interactions"] and
                profile.total_session_time >= threshold["time"]):
                return level
        
        return EngagementLevel.PASSIVE
    
    def _calculate_session_engagement_score(self, session: SessionAnalysis) -> float:
        """Calculate engagement score for a session (0.0 to 1.0)"""
        
        score = 0.0
        
        # Time-based score (up to 0.4)
        time_score = min(session.duration_seconds / 300, 1.0) * 0.4  # Max at 5 minutes
        
        # Interaction-based score (up to 0.4)
        interaction_score = min(session.interactions / 10, 1.0) * 0.4  # Max at 10 interactions
        
        # Journey depth score (up to 0.2)
        unique_interaction_types = len(set(interaction.split(':')[0] for interaction in session.journey_path))
        depth_score = min(unique_interaction_types / 5, 1.0) * 0.2  # Max at 5 different types
        
        score = time_score + interaction_score + depth_score
        
        # Conversion bonus
        if session.conversion_achieved:
            score = min(score * 1.5, 1.0)
        
        return score
    
    async def _check_analytics_events(self, event: InteractionEvent):
        """Check for significant analytics events and broadcast them"""
        
        visitor_profile = self.visitor_profiles.get(event.visitor_id)
        session = self.active_sessions.get(event.session_id)
        
        if not visitor_profile or not session:
            return
        
        # Broadcast engagement level changes
        total_interactions = sum(visitor_profile.interaction_patterns.values())
        if total_interactions in [3, 10, 25, 50]:  # Engagement milestones
            await websocket_manager.broadcast_event(WebSocketEvent(
                type=EventType.INTERACTION_RECORDED,
                data={
                    "visitor_engagement_level": visitor_profile.engagement_level.value,
                    "total_interactions": total_interactions,
                    "session_duration": session.duration_seconds
                },
                timestamp=datetime.utcnow(),
                source="analytics_processor",
                target_roles=[ConnectionRole.ADMIN]
            ))
        
        # Broadcast conversion events
        if self._is_conversion_event(event):
            await websocket_manager.broadcast_event(WebSocketEvent(
                type=EventType.INTERACTION_RECORDED,
                data={
                    "conversion_type": event.metadata.get("conversion_type", "unknown"),
                    "visitor_journey": visitor_profile.journey_segments,
                    "session_engagement_score": session.engagement_score
                },
                timestamp=datetime.utcnow(),
                source="analytics_processor",
                target_roles=[ConnectionRole.ADMIN]
            ))
    
    def get_engagement_metrics(self, hours: int = 24) -> EngagementMetrics:
        """Get comprehensive engagement metrics"""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            # Filter recent events
            recent_events = [e for e in self.interaction_events if e.timestamp >= cutoff]
            
            if not recent_events:
                return EngagementMetrics(
                    total_visitors=0,
                    unique_visitors_24h=0,
                    avg_session_duration=0,
                    bounce_rate=0,
                    pages_per_session=0,
                    conversion_rate=0,
                    engagement_distribution={level: 0 for level in EngagementLevel},
                    popular_content=[],
                    traffic_sources={},
                    device_breakdown={},
                    geographic_distribution={},
                    peak_hours=[],
                    retention_metrics={}
                )
            
            # Basic metrics
            unique_visitors = len(set(e.visitor_id for e in recent_events))
            total_visitors = len(self.visitor_profiles)
            
            # Session-based metrics
            recent_sessions = [s for s in self.active_sessions.values() if s.start_time >= cutoff]
            
            avg_session_duration = (
                sum(s.duration_seconds for s in recent_sessions) / len(recent_sessions)
                if recent_sessions else 0
            )
            
            bounce_rate = (
                sum(1 for s in recent_sessions if s.bounce_rate > 0) / len(recent_sessions)
                if recent_sessions else 0
            )
            
            pages_per_session = (
                sum(s.page_views for s in recent_sessions) / len(recent_sessions)
                if recent_sessions else 0
            )
            
            # Conversion rate
            conversions = sum(1 for s in recent_sessions if s.conversion_achieved)
            conversion_rate = conversions / len(recent_sessions) if recent_sessions else 0
            
            # Engagement distribution
            recent_visitors = {e.visitor_id for e in recent_events}
            engagement_distribution = {level: 0 for level in EngagementLevel}
            
            for visitor_id in recent_visitors:
                if visitor_id in self.visitor_profiles:
                    level = self.visitor_profiles[visitor_id].engagement_level
                    engagement_distribution[level] += 1
            
            # Popular content
            project_interactions = defaultdict(int)
            for event in recent_events:
                if "project_name" in event.metadata:
                    project_interactions[event.metadata["project_name"]] += 1
            
            popular_content = [
                {"project": project, "interactions": count}
                for project, count in sorted(project_interactions.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Traffic sources
            traffic_sources = defaultdict(int)
            for event in recent_events:
                if event.referrer:
                    # Extract domain from referrer
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(event.referrer).netloc
                        traffic_sources[domain] += 1
                    except:
                        traffic_sources["unknown"] += 1
                else:
                    traffic_sources["direct"] += 1
            
            # Device breakdown
            device_breakdown = defaultdict(int)
            for visitor_id in recent_visitors:
                if visitor_id in self.visitor_profiles:
                    device_type = self.visitor_profiles[visitor_id].device_info.get("device_type", "unknown")
                    device_breakdown[device_type] += 1
            
            # Peak hours
            hour_counts = defaultdict(int)
            for event in recent_events:
                hour_counts[event.timestamp.hour] += 1
            
            peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_hours = [hour for hour, count in peak_hours]
            
            # Retention metrics (simplified)
            retention_metrics = {
                "returning_visitors": len([v for v in self.visitor_profiles.values() if v.total_visits > 1]),
                "avg_sessions_per_visitor": sum(v.total_visits for v in self.visitor_profiles.values()) / len(self.visitor_profiles) if self.visitor_profiles else 0
            }
            
            return EngagementMetrics(
                total_visitors=total_visitors,
                unique_visitors_24h=unique_visitors,
                avg_session_duration=avg_session_duration,
                bounce_rate=bounce_rate,
                pages_per_session=pages_per_session,
                conversion_rate=conversion_rate,
                engagement_distribution=engagement_distribution,
                popular_content=popular_content,
                traffic_sources=dict(traffic_sources),
                device_breakdown=dict(device_breakdown),
                geographic_distribution={},  # Would need IP geolocation
                peak_hours=peak_hours,
                retention_metrics=retention_metrics
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate engagement metrics: {e}")
            return EngagementMetrics(
                total_visitors=0,
                unique_visitors_24h=0,
                avg_session_duration=0,
                bounce_rate=0,
                pages_per_session=0,
                conversion_rate=0,
                engagement_distribution={level: 0 for level in EngagementLevel},
                popular_content=[],
                traffic_sources={},
                device_breakdown={},
                geographic_distribution={},
                peak_hours=[],
                retention_metrics={}
            )
    
    def get_visitor_journey_analysis(self, visitor_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed journey analysis for a specific visitor"""
        
        if visitor_id not in self.visitor_profiles:
            return None
        
        profile = self.visitor_profiles[visitor_id]
        visitor_events = [e for e in self.interaction_events if e.visitor_id == visitor_id]
        
        if not visitor_events:
            return None
        
        # Sort events by timestamp
        visitor_events.sort(key=lambda e: e.timestamp)
        
        # Journey timeline
        journey_timeline = []
        for event in visitor_events:
            journey_timeline.append({
                "timestamp": event.timestamp.isoformat(),
                "interaction": event.interaction_type.value,
                "metadata": event.metadata,
                "page": event.page_url
            })
        
        # Session breakdown
        visitor_sessions = [s for s in self.active_sessions.values() if s.visitor_id == visitor_id]
        sessions_summary = []
        for session in visitor_sessions:
            sessions_summary.append({
                "session_id": session.session_id,
                "start_time": session.start_time.isoformat(),
                "duration": session.duration_seconds,
                "interactions": session.interactions,
                "engagement_score": session.engagement_score,
                "converted": session.conversion_achieved
            })
        
        return {
            "visitor_id": visitor_id,
            "profile": asdict(profile),
            "journey_timeline": journey_timeline,
            "sessions": sessions_summary,
            "insights": {
                "total_events": len(visitor_events),
                "most_active_hour": max(profile.preferred_times) if profile.preferred_times else None,
                "journey_completion_rate": len(profile.journey_segments) / len(self.journey_segments),
                "conversion_achieved": len(profile.conversion_events) > 0
            }
        }
    
    async def cleanup_old_data(self, retention_days: int = 30):
        """Clean up old analytics data based on retention policy"""
        
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        
        # Remove old interaction events
        self.interaction_events = [e for e in self.interaction_events if e.timestamp >= cutoff]
        
        # Remove old visitor profiles (keep only visitors active in retention period)
        active_visitors = set()
        for event in self.interaction_events:
            active_visitors.add(event.visitor_id)
        
        self.visitor_profiles = {
            vid: profile for vid, profile in self.visitor_profiles.items()
            if vid in active_visitors or profile.last_visit >= cutoff
        }
        
        # Remove old sessions
        self.active_sessions = {
            sid: session for sid, session in self.active_sessions.items()
            if session.start_time >= cutoff
        }
        
        logger.info(f"Analytics cleanup completed. Removed data older than {retention_days} days")
    
    def export_analytics_data(self) -> Dict[str, Any]:
        """Export analytics data for external analysis or backup"""
        
        return {
            "export_timestamp": datetime.utcnow().isoformat(),
            "visitor_profiles": {vid: asdict(profile) for vid, profile in self.visitor_profiles.items()},
            "recent_events": [asdict(event) for event in self.interaction_events[-1000:]],  # Last 1000 events
            "active_sessions": {sid: asdict(session) for sid, session in self.active_sessions.items()},
            "summary_stats": {
                "total_visitors": len(self.visitor_profiles),
                "total_events": len(self.interaction_events),
                "active_sessions": len(self.active_sessions)
            }
        }