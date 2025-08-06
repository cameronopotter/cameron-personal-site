"""
Skills-related Pydantic schemas
"""

from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID
from enum import Enum

from .base import BaseResponse, TimestampMixin, UUIDMixin


class SkillCategory(str, Enum):
    """Skill categories for organization"""
    FRONTEND = "frontend"
    BACKEND = "backend"
    DEVOPS = "devops" 
    DESIGN = "design"
    DATA_SCIENCE = "data_science"
    MOBILE = "mobile"
    GENERAL = "general"


class ConnectionType(str, Enum):
    """Types of connections between skills"""
    COMPLEMENT = "complement"       # Skills that work well together
    PREREQUISITE = "prerequisite"   # One skill leads to another
    SIMILAR = "similar"            # Skills in same domain
    SEQUENCE = "sequence"          # Learning progression


class SkillBase(BaseModel):
    """Base skill schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Skill name")
    category: SkillCategory = Field(..., description="Skill category")
    description: Optional[str] = Field(None, description="Skill description")
    
    # Constellation positioning
    constellation_group: Optional[str] = Field(None, max_length=50, description="Constellation group name")
    position_x: Optional[float] = Field(None, description="X position in constellation")
    position_y: Optional[float] = Field(None, description="Y position in constellation") 
    brightness: float = Field(default=0.5, ge=0, le=1, description="Visual prominence (0-1)")
    
    # Visual metadata
    icon_url: Optional[str] = Field(None, max_length=500, description="Icon URL")
    color_hex: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$", description="Hex color code")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "React",
                "category": "frontend",
                "description": "JavaScript library for building user interfaces",
                "constellation_group": "Frontend Frameworks",
                "position_x": 5.2,
                "position_y": -3.1,
                "brightness": 0.8,
                "icon_url": "https://cdn.example.com/react-icon.svg",
                "color_hex": "#61DAFB"
            }
        }
    )


class SkillCreate(SkillBase):
    """Schema for creating new skills"""
    proficiency_level: int = Field(1, ge=1, le=10, description="Proficiency level (1-10)")
    first_used_date: Optional[date] = Field(None, description="When skill was first used")


class SkillUpdate(BaseModel):
    """Schema for updating existing skills"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[SkillCategory] = None
    description: Optional[str] = None
    constellation_group: Optional[str] = Field(None, max_length=50)
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    brightness: Optional[float] = Field(None, ge=0, le=1)
    proficiency_level: Optional[int] = Field(None, ge=1, le=10)
    hours_practiced: Optional[int] = Field(None, ge=0)
    projects_used_in: Optional[int] = Field(None, ge=0)
    last_used_date: Optional[date] = None
    learning_velocity: Optional[float] = Field(None, ge=0)
    icon_url: Optional[str] = Field(None, max_length=500)
    color_hex: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")


class SkillResponse(SkillBase, UUIDMixin, TimestampMixin):
    """Complete skill response"""
    proficiency_level: int = Field(..., ge=1, le=10, description="Current proficiency (1-10)")
    hours_practiced: int = Field(default=0, description="Total hours practiced")
    projects_used_in: int = Field(default=0, description="Number of projects using this skill")
    
    # Learning progression
    first_used_date: Optional[date] = Field(None, description="First use date")
    last_used_date: Optional[date] = Field(None, description="Most recent use date")
    learning_velocity: float = Field(default=0.0, description="Learning speed indicator")


class SkillConnectionBase(BaseModel):
    """Base skill connection schema"""
    skill_a_id: UUID = Field(..., description="First skill ID")
    skill_b_id: UUID = Field(..., description="Second skill ID")
    connection_type: ConnectionType = Field(..., description="Type of connection")
    strength: float = Field(default=0.5, ge=0, le=1, description="Connection strength (0-1)")
    
    @validator('skill_b_id')
    def validate_different_skills(cls, v, values):
        if 'skill_a_id' in values and v == values['skill_a_id']:
            raise ValueError('skill_a_id and skill_b_id must be different')
        return v


class SkillConnectionCreate(SkillConnectionBase):
    """Schema for creating skill connections"""
    pass


class SkillConnectionResponse(SkillConnectionBase, UUIDMixin, TimestampMixin):
    """Skill connection response with metadata"""
    projects_combined: int = Field(default=0, description="Projects using both skills")
    learning_correlation: Optional[float] = Field(None, description="Learning correlation coefficient")
    
    # Include skill details for easier frontend consumption
    skill_a: Optional[SkillResponse] = None
    skill_b: Optional[SkillResponse] = None


class ConstellationResponse(BaseModel):
    """Response for a skill constellation grouping"""
    constellation_name: str = Field(..., description="Constellation group name")
    skills: List[SkillResponse] = Field(..., description="Skills in this constellation")
    connections: List[SkillConnectionResponse] = Field(..., description="Connections between skills")
    center_position: Dict[str, float] = Field(..., description="Center coordinates of constellation")
    total_proficiency: float = Field(..., description="Combined proficiency score")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "constellation_name": "Frontend Frameworks",
                "skills": [],
                "connections": [],
                "center_position": {"x": 0.0, "y": 0.0},
                "total_proficiency": 7.5
            }
        }
    )


class SkillProgressUpdate(BaseModel):
    """Schema for updating skill progress"""
    proficiency_delta: Optional[int] = Field(None, description="Change in proficiency level")
    hours_practiced_delta: int = Field(0, ge=0, description="Additional hours practiced")
    projects_used_delta: int = Field(0, ge=0, description="Additional projects using this skill")
    learning_notes: Optional[str] = Field(None, description="Learning progress notes")


class SkillAnalytics(BaseModel):
    """Analytics data for skills"""
    total_skills: int = Field(..., description="Total number of skills")
    average_proficiency: float = Field(..., description="Average proficiency across all skills")
    most_used_categories: List[Dict[str, Any]] = Field(..., description="Most frequently used skill categories")
    learning_velocity_trend: List[Dict[str, Any]] = Field(..., description="Learning velocity over time")
    skill_connections_count: int = Field(..., description="Total skill connections")
    top_skill_combinations: List[Dict[str, Any]] = Field(..., description="Most common skill combinations in projects")