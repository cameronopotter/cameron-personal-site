"""
Project models for the Digital Garden
"""

from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime, Boolean,
    ForeignKey, CheckConstraint, Index, func
)
# No PostgreSQL-specific types needed for SQLite
from sqlalchemy.orm import relationship
from .base import Base, BaseModel
import uuid


class Project(Base, BaseModel):
    """
    Digital Garden Projects - The plants in our garden
    Each project represents a software project with garden metaphor properties
    """
    __tablename__ = "projects"

    # Basic project information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    github_repo = Column(String(255))
    demo_url = Column(String(500))

    # Garden metaphor fields
    plant_type = Column(String(50), default='generic')  # tree, flower, vine, etc.
    growth_stage = Column(String(20), default='seed')   # seed, sprout, growing, blooming, mature
    planted_date = Column(DateTime(timezone=True), server_default=func.now())

    # 3D positioning in the garden
    position_x = Column(Float, default=0.0)
    position_y = Column(Float, default=0.0)  
    position_z = Column(Float, default=0.0)

    # Growth factors that influence plant development
    commit_count = Column(Integer, default=0)
    lines_of_code = Column(Integer, default=0)
    complexity_score = Column(Float, default=0.0)
    visitor_interactions = Column(Integer, default=0)

    # Technical and organizational metadata
    technologies = Column(Text)  # JSON string of tech stack items
    status = Column(String(20), default='active')      # active, archived, featured
    visibility = Column(String(20), default='public')  # public, private, unlisted

    # Relationships
    growth_logs = relationship(
        "ProjectGrowthLog",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("growth_stage IN ('seed', 'sprout', 'growing', 'blooming', 'mature')", name='check_growth_stage'),
        CheckConstraint("status IN ('active', 'archived', 'featured')", name='check_status'),
        CheckConstraint("visibility IN ('public', 'private', 'unlisted')", name='check_visibility'),
        CheckConstraint("plant_type IN ('tree', 'flower', 'vine', 'shrub', 'herb', 'generic')", name='check_plant_type'),
        Index('idx_projects_growth_stage', 'growth_stage'),
        Index('idx_projects_status', 'status'),
        Index('idx_projects_planted_date', 'planted_date'),
        Index('idx_projects_position', 'position_x', 'position_y', 'position_z'),
    )

    def __repr__(self):
        return f"<Project(name='{self.name}', growth_stage='{self.growth_stage}')>"


class ProjectGrowthLog(Base, BaseModel):
    """
    Growth history tracking for projects
    Records changes in project metrics and growth stages over time
    """
    __tablename__ = "project_growth_log"

    # Link to project
    project_id = Column(
        String(36), 
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False
    )

    # Growth metrics snapshot (deltas from previous measurement)
    commits_delta = Column(Integer, default=0)
    lines_added = Column(Integer, default=0)
    lines_removed = Column(Integer, default=0)
    complexity_change = Column(Float, default=0.0)

    # External activity data (stored as JSON for flexibility)
    github_activity = Column(Text)       # JSON: commits, PRs, issues
    deployment_events = Column(Text)     # JSON: deployments, releases

    # Visitor engagement metrics
    page_views = Column(Integer, default=0)
    interactions = Column(Integer, default=0)
    time_spent_minutes = Column(Integer, default=0)

    # Growth calculation results
    previous_stage = Column(String(20))
    new_stage = Column(String(20))
    growth_factor = Column(Float)        # 0-1 scale indicating growth progress

    # Timing
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="growth_logs")

    # Constraints and indexes
    __table_args__ = (
        CheckConstraint("growth_factor >= 0 AND growth_factor <= 1", name='check_growth_factor_range'),
        Index('idx_growth_log_project', 'project_id'),
        Index('idx_growth_log_recorded', 'recorded_at'),
        Index('idx_growth_log_project_recorded', 'project_id', 'recorded_at'),
    )

    def __repr__(self):
        return f"<ProjectGrowthLog(project_id='{self.project_id}', new_stage='{self.new_stage}')>"