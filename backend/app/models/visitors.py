"""
Visitor session models for engagement analytics
"""

from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime, Boolean,
    CheckConstraint, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from .base import Base, BaseModel


class VisitorSession(Base, BaseModel):
    """
    Visitor session tracking for engagement analytics
    Privacy-focused tracking with anonymized data
    """
    __tablename__ = "visitor_sessions"

    # Session identification (anonymized)
    session_token = Column(String(255), unique=True, nullable=False)

    # Anonymized visitor information  
    user_agent = Column(Text)
    ip_hash = Column(String(64))         # Hashed IP for privacy compliance
    country_code = Column(String(2))

    # Garden interaction data
    projects_viewed = Column(ARRAY(UUID))                    # Array of project UUIDs
    time_spent_per_project = Column(JSONB)                   # {project_id: seconds}
    interaction_events = Column(ARRAY(JSONB))                # Array of interaction event objects

    # Navigation and journey tracking
    entry_point = Column(String(255))                        # Referrer or entry URL
    journey_path = Column(ARRAY(Text))                       # Sequence of areas visited
    exit_point = Column(String(255))                         # Last area before leaving

    # Engagement metrics
    total_time_seconds = Column(Integer, default=0)
    scroll_depth_percent = Column(Float, CheckConstraint("scroll_depth_percent >= 0 AND scroll_depth_percent <= 100"))
    clicks_count = Column(Integer, default=0)
    seeds_planted = Column(Integer, default=0)               # Interactive elements engaged with

    # Device and browser information
    device_type = Column(String(20))                         # 'desktop', 'tablet', 'mobile'
    browser = Column(String(50))
    screen_resolution = Column(String(20))                   # e.g., "1920x1080"

    # Session timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))

    # Constraints and indexes
    __table_args__ = (
        CheckConstraint("device_type IN ('desktop', 'tablet', 'mobile', 'unknown')", name='check_device_type'),
        CheckConstraint("total_time_seconds >= 0", name='check_positive_time'),
        CheckConstraint("clicks_count >= 0", name='check_positive_clicks'),
        CheckConstraint("seeds_planted >= 0", name='check_positive_seeds'),
        CheckConstraint("started_at <= last_activity_at", name='check_activity_time_order'),
        Index('idx_visitor_sessions_started', 'started_at'),
        Index('idx_visitor_sessions_device', 'device_type'),
        Index('idx_visitor_sessions_country', 'country_code'),
        Index('idx_visitor_sessions_active', 'started_at', 'ended_at'),
        Index('idx_visitor_sessions_token', 'session_token'),
    )

    def __repr__(self):
        return f"<VisitorSession(session_token='{self.session_token[:8]}...', device_type='{self.device_type}')>"

    @property
    def is_active(self) -> bool:
        """Check if session is still active"""
        return self.ended_at is None

    @property
    def session_duration_minutes(self) -> float:
        """Calculate session duration in minutes"""
        if self.ended_at:
            delta = self.ended_at - self.started_at
        else:
            # Ongoing session
            from datetime import datetime
            delta = datetime.utcnow() - self.started_at
        return delta.total_seconds() / 60

    @property
    def engagement_score(self) -> float:
        """
        Calculate engagement score based on multiple factors
        Returns a score between 0 and 1
        """
        if self.total_time_seconds == 0:
            return 0.0

        # Base score from time spent (normalized to reasonable session length)
        time_score = min(self.total_time_seconds / 1800, 1.0)  # 30 minutes = max time score

        # Interaction intensity (clicks per minute)
        click_rate = self.clicks_count / (self.total_time_seconds / 60) if self.total_time_seconds > 60 else 0
        interaction_score = min(click_rate / 10, 1.0)  # 10 clicks/minute = max interaction score

        # Content exploration (number of projects viewed)
        exploration_score = min(len(self.projects_viewed or []) / 10, 1.0) if self.projects_viewed else 0

        # Scroll depth contribution
        scroll_score = (self.scroll_depth_percent or 0) / 100

        # Seeds planted (active engagement)
        seed_score = min((self.seeds_planted or 0) / 5, 1.0)  # 5 seeds = max seed score

        # Weighted combination
        engagement = (
            time_score * 0.25 +
            interaction_score * 0.25 +
            exploration_score * 0.2 + 
            scroll_score * 0.15 +
            seed_score * 0.15
        )

        return round(engagement, 3)