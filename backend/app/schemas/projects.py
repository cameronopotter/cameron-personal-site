"""
Project-related Pydantic schemas
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

from .base import BaseResponse, Position3D, TimestampMixin, UUIDMixin


class GrowthStage(str, Enum):
    """Project growth stages"""
    SEED = "seed"
    SPROUT = "sprout" 
    GROWING = "growing"
    BLOOMING = "blooming"
    MATURE = "mature"


class PlantType(str, Enum):
    """Types of plants in the garden"""
    TREE = "tree"
    FLOWER = "flower"
    VINE = "vine"
    SHRUB = "shrub" 
    HERB = "herb"
    GENERIC = "generic"


class ProjectStatus(str, Enum):
    """Project status options"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    FEATURED = "featured"


class ProjectVisibility(str, Enum):
    """Project visibility options"""
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"


class ProjectBase(BaseModel):
    """Base project schema with core fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    github_repo: Optional[str] = Field(None, max_length=255, description="GitHub repository URL")
    demo_url: Optional[str] = Field(None, max_length=500, description="Live demo URL")
    
    # Garden metaphor fields
    plant_type: PlantType = Field(default=PlantType.GENERIC, description="Type of plant representation")
    
    # 3D positioning
    position_x: float = Field(default=0.0, description="X position in garden")
    position_y: float = Field(default=0.0, description="Y position in garden")
    position_z: float = Field(default=0.0, description="Z position in garden")
    
    # Metadata
    technologies: Optional[List[str]] = Field(default=[], description="Technology stack")
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE, description="Project status")
    visibility: ProjectVisibility = Field(default=ProjectVisibility.PUBLIC, description="Project visibility")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Digital Greenhouse",
                "description": "An interactive 3D personal portfolio site",
                "github_repo": "https://github.com/user/digital-greenhouse",
                "demo_url": "https://greenhouse.example.com",
                "plant_type": "tree",
                "position_x": 10.5,
                "position_y": 2.0,
                "position_z": -5.3,
                "technologies": ["React", "Three.js", "FastAPI", "PostgreSQL"],
                "status": "active",
                "visibility": "public"
            }
        }
    )


class ProjectCreate(ProjectBase):
    """Schema for creating new projects"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating existing projects"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    github_repo: Optional[str] = Field(None, max_length=255)
    demo_url: Optional[str] = Field(None, max_length=500)
    plant_type: Optional[PlantType] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    position_z: Optional[float] = None
    technologies: Optional[List[str]] = None
    status: Optional[ProjectStatus] = None
    visibility: Optional[ProjectVisibility] = None


class ProjectResponse(ProjectBase, UUIDMixin, TimestampMixin):
    """Complete project response with all fields"""
    growth_stage: GrowthStage = Field(..., description="Current growth stage")
    planted_date: datetime = Field(..., description="When project was first created")
    
    # Growth metrics
    commit_count: int = Field(default=0, description="Total commit count")
    lines_of_code: int = Field(default=0, description="Total lines of code")
    complexity_score: float = Field(default=0.0, description="Calculated complexity score")
    visitor_interactions: int = Field(default=0, description="Total visitor interactions")


class ProjectGrowthLogResponse(UUIDMixin, TimestampMixin):
    """Project growth log entry response"""
    project_id: UUID = Field(..., description="Associated project ID")
    
    # Growth deltas
    commits_delta: int = Field(default=0, description="Commits added since last measurement")
    lines_added: int = Field(default=0, description="Lines of code added")
    lines_removed: int = Field(default=0, description="Lines of code removed")
    complexity_change: float = Field(default=0.0, description="Change in complexity score")
    
    # External activity
    github_activity: Optional[Dict[str, Any]] = Field(default={}, description="GitHub activity data")
    deployment_events: Optional[Dict[str, Any]] = Field(default={}, description="Deployment events data")
    
    # Visitor engagement
    page_views: int = Field(default=0, description="Page views in this period")
    interactions: int = Field(default=0, description="Visitor interactions")
    time_spent_minutes: int = Field(default=0, description="Time spent by visitors")
    
    # Growth calculation results
    previous_stage: Optional[GrowthStage] = Field(None, description="Previous growth stage")
    new_stage: Optional[GrowthStage] = Field(None, description="New growth stage")
    growth_factor: Optional[float] = Field(None, ge=0, le=1, description="Growth progress (0-1)")
    
    recorded_at: datetime = Field(..., description="When this growth was recorded")


class SeedPlantingRequest(BaseModel):
    """Request to plant a new project seed"""
    project_data: ProjectCreate = Field(..., description="Project information")
    position: Position3D = Field(..., description="3D position to plant the seed")
    initial_growth_factor: Optional[float] = Field(0.0, ge=0, le=1, description="Initial growth progress")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_data": {
                    "name": "New Project",
                    "description": "A revolutionary new idea",
                    "plant_type": "flower",
                    "technologies": ["Python", "FastAPI"]
                },
                "position": {"x": 5.0, "y": 0.0, "z": 3.0},
                "initial_growth_factor": 0.1
            }
        }
    )


class PlantedSeedResponse(BaseResponse):
    """Response after planting a new seed"""
    project: ProjectResponse = Field(..., description="Created project")
    growth_triggered: bool = Field(default=False, description="Whether growth calculation was triggered")
    estimated_growth_time: Optional[int] = Field(None, description="Estimated minutes until next growth stage")


class InteractionEvent(BaseModel):
    """Visitor interaction with a project"""
    interaction_type: str = Field(..., description="Type of interaction")
    duration_seconds: Optional[int] = Field(None, ge=0, description="Duration of interaction")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional interaction data")
    
    @field_validator('interaction_type')
    @classmethod
    def validate_interaction_type(cls, v):
        allowed_types = [
            'view', 'click', 'hover', 'scroll', 'zoom', 'rotate',
            'demo_launch', 'github_visit', 'seed_plant', 'growth_trigger'
        ]
        if v not in allowed_types:
            raise ValueError(f'Interaction type must be one of: {allowed_types}')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "interaction_type": "demo_launch",
                "duration_seconds": 45,
                "metadata": {
                    "button_clicked": "Live Demo",
                    "page_section": "project_card"
                }
            }
        }
    )


class InteractionResponse(BaseResponse):
    """Response after recording an interaction"""
    interaction_recorded: bool = Field(default=True, description="Whether interaction was recorded")
    growth_triggered: bool = Field(default=False, description="Whether interaction triggered growth")
    new_growth_stage: Optional[GrowthStage] = Field(None, description="New growth stage if changed")
    engagement_score_delta: Optional[float] = Field(None, description="Change in engagement score")


class ProjectDetailResponse(ProjectResponse):
    """Detailed project response with growth history and analytics"""
    growth_logs: Optional[List[ProjectGrowthLogResponse]] = Field(default=[], description="Growth history")
    related_skills: Optional[List[str]] = Field(default=[], description="Related skills")
    engagement_metrics: Optional[Dict[str, Any]] = Field(default={}, description="Engagement analytics")
    recent_activity: Optional[Dict[str, Any]] = Field(default={}, description="Recent GitHub/deployment activity")