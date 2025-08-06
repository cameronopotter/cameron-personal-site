"""
Skills models for the constellation system
"""

from sqlalchemy import (
    Column, String, Text, Integer, Float, Date, DateTime, Boolean,
    ForeignKey, CheckConstraint, Index, UniqueConstraint, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, BaseModel
import uuid


class Skill(Base, BaseModel):
    """
    Skills constellation system
    Each skill is positioned as a star in various constellations
    """
    __tablename__ = "skills"

    # Basic skill information
    name = Column(String(100), nullable=False)
    category = Column(String(50))  # 'frontend', 'backend', 'devops', 'design'
    description = Column(Text)

    # Constellation positioning (3D space for dynamic visualizations)
    constellation_group = Column(String(50))  # Which constellation this belongs to
    position_x = Column(Float)
    position_y = Column(Float)
    brightness = Column(Float, default=0.5)  # 0-1 scale for visual prominence

    # Proficiency and usage tracking
    proficiency_level = Column(Integer, CheckConstraint("proficiency_level >= 1 AND proficiency_level <= 10"))
    hours_practiced = Column(Integer, default=0)
    projects_used_in = Column(Integer, default=0)

    # Learning progression over time
    first_used_date = Column(Date)
    last_used_date = Column(Date)
    learning_velocity = Column(Float, default=0.0)  # How fast skill is improving

    # Visual and presentation metadata
    icon_url = Column(String(500))
    color_hex = Column(String(7))  # Hex color code for visualization

    # Relationships
    connections_as_skill_a = relationship(
        "SkillConnection",
        foreign_keys="SkillConnection.skill_a_id",
        back_populates="skill_a",
        cascade="all, delete-orphan"
    )
    connections_as_skill_b = relationship(
        "SkillConnection", 
        foreign_keys="SkillConnection.skill_b_id",
        back_populates="skill_b",
        cascade="all, delete-orphan"
    )

    # Constraints and indexes
    __table_args__ = (
        CheckConstraint("brightness >= 0 AND brightness <= 1", name='check_brightness_range'),
        CheckConstraint("learning_velocity >= 0", name='check_learning_velocity_positive'),
        Index('idx_skills_category', 'category'),
        Index('idx_skills_constellation', 'constellation_group'),
        Index('idx_skills_proficiency', 'proficiency_level'),
        Index('idx_skills_position', 'position_x', 'position_y'),
    )

    def __repr__(self):
        return f"<Skill(name='{self.name}', category='{self.category}', proficiency={self.proficiency_level})>"


class SkillConnection(Base, BaseModel):
    """
    Connections between skills in the constellation
    Represents how skills relate to and complement each other
    """
    __tablename__ = "skill_connections"

    # Connected skills
    skill_a_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('skills.id', ondelete='CASCADE'),
        nullable=False
    )
    skill_b_id = Column(
        UUID(as_uuid=True),
        ForeignKey('skills.id', ondelete='CASCADE'), 
        nullable=False
    )

    # Connection properties
    connection_type = Column(String(50))  # 'complement', 'prerequisite', 'similar', 'sequence'
    strength = Column(Float, default=0.5)  # 0-1 scale for connection visibility/weight

    # Evidence and metrics supporting this connection
    projects_combined = Column(Integer, default=0)      # How many projects used both skills
    learning_correlation = Column(Float)                # Statistical correlation in learning patterns

    # Relationships
    skill_a = relationship("Skill", foreign_keys=[skill_a_id], back_populates="connections_as_skill_a")
    skill_b = relationship("Skill", foreign_keys=[skill_b_id], back_populates="connections_as_skill_b")

    # Constraints and indexes
    __table_args__ = (
        CheckConstraint("strength >= 0 AND strength <= 1", name='check_strength_range'),
        CheckConstraint("skill_a_id != skill_b_id", name='check_no_self_connection'),
        CheckConstraint("connection_type IN ('complement', 'prerequisite', 'similar', 'sequence')", name='check_connection_type'),
        UniqueConstraint('skill_a_id', 'skill_b_id', name='unique_skill_connection'),
        Index('idx_skill_connections_type', 'connection_type'),
        Index('idx_skill_connections_strength', 'strength'),
    )

    def __repr__(self):
        return f"<SkillConnection(skill_a_id='{self.skill_a_id}', skill_b_id='{self.skill_b_id}', type='{self.connection_type}')>"