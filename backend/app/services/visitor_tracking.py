"""
Visitor tracking and session management service
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging

from app.core.database import get_async_db
from app.models.visitors import VisitorSession

logger = logging.getLogger(__name__)


def generate_session_token() -> str:
    """Generate a secure anonymous session token"""
    return f"anon_sess_{secrets.token_urlsafe(16)}"


def hash_ip_address(ip_address: str) -> str:
    """Hash IP address for privacy-compliant storage"""
    # Add salt to prevent rainbow table attacks
    salt = "digital_greenhouse_salt_2024"
    return hashlib.sha256(f"{ip_address}{salt}".encode()).hexdigest()


def parse_user_agent(user_agent: str) -> Dict[str, Optional[str]]:
    """Parse user agent string to extract device and browser info"""
    user_agent_lower = user_agent.lower()
    
    # Determine device type
    if any(mobile in user_agent_lower for mobile in ['mobile', 'android', 'iphone']):
        device_type = 'mobile'
    elif any(tablet in user_agent_lower for tablet in ['tablet', 'ipad']):
        device_type = 'tablet'
    elif any(desktop in user_agent_lower for desktop in ['windows', 'macintosh', 'linux', 'x11']):
        device_type = 'desktop'
    else:
        device_type = 'unknown'
    
    # Determine browser
    if 'chrome' in user_agent_lower:
        browser = 'Chrome'
    elif 'firefox' in user_agent_lower:
        browser = 'Firefox'
    elif 'safari' in user_agent_lower:
        browser = 'Safari'
    elif 'edge' in user_agent_lower:
        browser = 'Edge'
    else:
        browser = 'Other'
    
    return {
        'device_type': device_type,
        'browser': browser
    }


async def create_visitor_session(
    request: Request,
    db: AsyncSession
) -> VisitorSession:
    """Create a new visitor session"""
    
    # Extract request information
    user_agent = request.headers.get('user-agent', '')
    client_ip = request.client.host if request.client else 'unknown'
    
    # Parse user agent
    parsed_ua = parse_user_agent(user_agent)
    
    # Create session
    session = VisitorSession(
        session_token=generate_session_token(),
        user_agent=user_agent,
        ip_hash=hash_ip_address(client_ip),
        device_type=parsed_ua['device_type'],
        browser=parsed_ua['browser'],
        started_at=datetime.utcnow(),
        last_activity_at=datetime.utcnow()
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    logger.info(f"New visitor session created: {session.session_token}")
    return session


async def get_or_create_visitor_session(
    request: Request,
    db: AsyncSession = Depends(get_async_db)
) -> str:
    """Get existing session or create new one"""
    
    # Try to get session token from various sources
    session_token = None
    
    # Check query parameter first
    session_token = request.query_params.get('session_token')
    
    # Check headers
    if not session_token:
        session_token = request.headers.get('X-Session-Token')
    
    # Check cookies (if implemented)
    if not session_token:
        session_token = request.cookies.get('visitor_session')
    
    # If we have a token, try to find existing session
    if session_token:
        result = await db.execute(
            select(VisitorSession)
            .where(VisitorSession.session_token == session_token)
        )
        session = result.scalar_one_or_none()
        
        if session and session.is_active:
            # Update last activity
            session.last_activity_at = datetime.utcnow()
            await db.commit()
            return session.session_token
    
    # Create new session
    session = await create_visitor_session(request, db)
    return session.session_token


class VisitorTrackingService:
    """Service for visitor analytics and tracking"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def update_session_activity(
        self,
        session_token: str,
        activity_data: Dict[str, Any]
    ) -> bool:
        """Update visitor session with new activity"""
        
        result = await self.db.execute(
            select(VisitorSession)
            .where(VisitorSession.session_token == session_token)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return False
        
        # Update session data
        if 'scroll_depth' in activity_data:
            session.scroll_depth_percent = max(
                session.scroll_depth_percent or 0,
                activity_data['scroll_depth']
            )
        
        if 'journey_path' in activity_data:
            current_path = session.journey_path or []
            new_location = activity_data['journey_path']
            if not current_path or current_path[-1] != new_location:
                current_path.append(new_location)
                session.journey_path = current_path
        
        if 'time_spent' in activity_data:
            session.total_time_seconds += activity_data['time_spent']
        
        session.last_activity_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def end_session(self, session_token: str) -> bool:
        """Mark session as ended"""
        
        result = await self.db.execute(
            select(VisitorSession)
            .where(VisitorSession.session_token == session_token)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return False
        
        session.ended_at = datetime.utcnow()
        await self.db.commit()
        
        logger.info(f"Session ended: {session_token[:16]}...")
        return True
    
    async def get_session_analytics(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get analytics for a specific session"""
        
        result = await self.db.execute(
            select(VisitorSession)
            .where(VisitorSession.session_token == session_token)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return None
        
        return {
            "session_token": session.session_token,
            "duration_minutes": session.session_duration_minutes,
            "engagement_score": session.engagement_score,
            "projects_viewed": len(session.projects_viewed or []),
            "total_interactions": len(session.interaction_events or []),
            "device_type": session.device_type,
            "country": session.country_code,
            "is_active": session.is_active
        }
    
    async def get_visitor_analytics_summary(
        self,
        hours_back: int = 24
    ) -> Dict[str, Any]:
        """Get summary analytics for recent visitors"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Total sessions
        result = await self.db.execute(
            select(func.count(VisitorSession.id))
            .where(VisitorSession.started_at >= cutoff_time)
        )
        total_sessions = result.scalar() or 0
        
        # Active sessions
        result = await self.db.execute(
            select(func.count(VisitorSession.id))
            .where(
                VisitorSession.started_at >= cutoff_time,
                VisitorSession.ended_at.is_(None)
            )
        )
        active_sessions = result.scalar() or 0
        
        # Average engagement
        result = await self.db.execute(
            select(func.avg(VisitorSession.engagement_score))
            .where(VisitorSession.started_at >= cutoff_time)
        )
        avg_engagement = result.scalar() or 0
        
        # Device breakdown
        result = await self.db.execute(
            select(VisitorSession.device_type, func.count(VisitorSession.id))
            .where(VisitorSession.started_at >= cutoff_time)
            .group_by(VisitorSession.device_type)
        )
        device_breakdown = dict(result.fetchall())
        
        # Popular projects (based on views)
        result = await self.db.execute(
            select(
                func.unnest(VisitorSession.projects_viewed).label('project_id'),
                func.count().label('views')
            )
            .where(VisitorSession.started_at >= cutoff_time)
            .group_by('project_id')
            .order_by(func.count().desc())
            .limit(10)
        )
        popular_projects = [
            {"project_id": str(project_id), "views": views}
            for project_id, views in result.fetchall()
        ]
        
        return {
            "time_period_hours": hours_back,
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "average_engagement_score": float(avg_engagement),
            "device_breakdown": device_breakdown,
            "popular_projects": popular_projects
        }
    
    async def identify_returning_visitors(self) -> List[Dict[str, Any]]:
        """Identify patterns that suggest returning visitors"""
        
        # Look for similar IP hashes, user agents, or behavior patterns
        # This is a simplified implementation
        
        result = await self.db.execute(
            select(
                VisitorSession.ip_hash,
                func.count(VisitorSession.id).label('session_count'),
                func.avg(VisitorSession.engagement_score).label('avg_engagement')
            )
            .group_by(VisitorSession.ip_hash)
            .having(func.count(VisitorSession.id) > 1)
            .order_by(func.count(VisitorSession.id).desc())
        )
        
        returning_patterns = []
        for ip_hash, session_count, avg_engagement in result.fetchall():
            returning_patterns.append({
                "ip_hash": ip_hash[:8] + "...",  # Truncate for privacy
                "session_count": session_count,
                "average_engagement": float(avg_engagement or 0)
            })
        
        return returning_patterns
    
    async def get_journey_patterns(self) -> List[Dict[str, Any]]:
        """Analyze common visitor journey patterns"""
        
        # Get common journey paths
        result = await self.db.execute(
            select(
                VisitorSession.journey_path,
                func.count(VisitorSession.id).label('frequency')
            )
            .where(VisitorSession.journey_path.isnot(None))
            .group_by(VisitorSession.journey_path)
            .order_by(func.count(VisitorSession.id).desc())
            .limit(10)
        )
        
        journey_patterns = []
        for journey_path, frequency in result.fetchall():
            if journey_path:
                journey_patterns.append({
                    "path": journey_path,
                    "frequency": frequency
                })
        
        return journey_patterns
    
    async def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up old visitor sessions for privacy compliance"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Delete old sessions
        result = await self.db.execute(
            select(func.count(VisitorSession.id))
            .where(VisitorSession.started_at < cutoff_date)
        )
        count_to_delete = result.scalar() or 0
        
        if count_to_delete > 0:
            await self.db.execute(
                VisitorSession.__table__.delete()
                .where(VisitorSession.started_at < cutoff_date)
            )
            await self.db.commit()
            
            logger.info(f"Cleaned up {count_to_delete} old visitor sessions")
        
        return count_to_delete