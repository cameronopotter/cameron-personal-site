"""
Garden state and ecosystem Pydantic schemas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

from .base import BaseResponse, Position3D
from .projects import ProjectResponse, GrowthStage
from .skills import SkillResponse, ConstellationResponse
from .weather import WeatherStateResponse
from .visitors import VisitorAnalytics


class GardenState(BaseResponse):
    """Complete garden ecosystem state"""
    
    # Core garden elements
    projects: List[ProjectResponse] = Field(..., description="All projects in the garden")
    skills_constellations: List[ConstellationResponse] = Field(..., description="Skill constellation groupings")
    current_weather: WeatherStateResponse = Field(..., description="Current weather state")
    
    # Garden metadata
    garden_age_days: int = Field(..., description="Days since garden creation")
    total_growth_events: int = Field(..., description="Total growth stage changes")
    active_projects_count: int = Field(..., description="Number of active projects")
    
    # Visual and environmental state
    season: str = Field(..., description="Current garden season")
    time_of_day: str = Field(..., description="Current time of day")
    ambient_conditions: Dict[str, Any] = Field(..., description="Environmental conditions")
    
    # Personalization data (if visitor session provided)
    personalized_highlights: Optional[List[str]] = Field(None, description="Personalized content highlights")
    recommended_projects: Optional[List[ProjectResponse]] = Field(None, description="Recommended projects for visitor")
    visitor_journey_suggestion: Optional[str] = Field(None, description="Suggested navigation path")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Garden state retrieved successfully",
                "timestamp": "2024-01-01T12:00:00Z",
                "projects": [],
                "skills_constellations": [],
                "current_weather": {},
                "garden_age_days": 365,
                "total_growth_events": 42,
                "active_projects_count": 12,
                "season": "spring",
                "time_of_day": "day",
                "ambient_conditions": {
                    "light_intensity": 0.8,
                    "wind_speed": 0.3,
                    "humidity": 0.6
                },
                "personalized_highlights": [
                    "New growth in React projects",
                    "Backend skills constellation is bright tonight"
                ],
                "recommended_projects": [],
                "visitor_journey_suggestion": "Start with the Featured Projects constellation"
            }
        }
    )


class GardenSummaryResponse(BaseResponse):
    """Condensed garden overview for quick loading"""
    project_count_by_stage: Dict[GrowthStage, int] = Field(..., description="Project counts by growth stage")
    total_technologies: int = Field(..., description="Total unique technologies")
    weather_summary: Dict[str, Any] = Field(..., description="Weather state summary")
    recent_growth_events: List[Dict[str, Any]] = Field(..., description="Recent growth activities")
    top_skills: List[str] = Field(..., description="Top skills by proficiency")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "project_count_by_stage": {
                    "seed": 2,
                    "sprout": 3,
                    "growing": 4,
                    "blooming": 2,
                    "mature": 1
                },
                "total_technologies": 18,
                "weather_summary": {
                    "type": "aurora",
                    "intensity": 0.7,
                    "duration_hours": 2.5
                },
                "recent_growth_events": [
                    {
                        "project_name": "Digital Greenhouse",
                        "from_stage": "growing", 
                        "to_stage": "blooming",
                        "timestamp": "2024-01-01T10:00:00Z"
                    }
                ],
                "top_skills": ["Python", "React", "PostgreSQL", "Docker", "AWS"]
            }
        }
    )


class GardenEvolution(BaseModel):
    """Garden evolution and growth timeline"""
    timeline_events: List[Dict[str, Any]] = Field(..., description="Chronological garden events")
    growth_velocity: float = Field(..., description="Overall growth rate")
    seasonal_patterns: Dict[str, Any] = Field(..., description="Seasonal growth patterns")
    milestone_achievements: List[Dict[str, Any]] = Field(..., description="Major milestones reached")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timeline_events": [
                    {
                        "type": "project_planted",
                        "project_name": "First API",
                        "timestamp": "2023-06-01T00:00:00Z",
                        "details": {"initial_stage": "seed", "technologies": ["FastAPI", "Python"]}
                    },
                    {
                        "type": "growth_milestone",
                        "project_name": "First API", 
                        "timestamp": "2023-07-15T00:00:00Z",
                        "details": {"stage_change": "seed_to_sprout", "trigger": "first_commit"}
                    }
                ],
                "growth_velocity": 1.2,
                "seasonal_patterns": {
                    "spring": {"growth_rate": 1.4, "new_projects": 3},
                    "summer": {"growth_rate": 1.1, "new_projects": 2},
                    "autumn": {"growth_rate": 0.9, "new_projects": 1},
                    "winter": {"growth_rate": 1.3, "new_projects": 4}
                },
                "milestone_achievements": [
                    {
                        "milestone": "first_mature_project",
                        "achieved_at": "2023-09-01T00:00:00Z",
                        "project_name": "Portfolio Site"
                    }
                ]
            }
        }
    )


class GardenInteractionSuggestion(BaseModel):
    """Suggested interactions for visitors"""
    suggestion_type: str = Field(..., description="Type of suggestion")
    title: str = Field(..., description="Suggestion title")
    description: str = Field(..., description="Suggestion description")
    target_element: Dict[str, Any] = Field(..., description="Element to interact with")
    expected_outcome: str = Field(..., description="What will happen")
    difficulty: str = Field(..., description="Interaction difficulty level")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "suggestion_type": "plant_seed",
                "title": "Plant Your First Seed",
                "description": "Click on an empty spot in the garden to plant a new project seed",
                "target_element": {
                    "type": "garden_space",
                    "coordinates": {"x": 5.0, "y": 0.0, "z": 2.0}
                },
                "expected_outcome": "A new seed will appear and begin growing based on your input",
                "difficulty": "easy"
            }
        }
    )


class GardenHealth(BaseModel):
    """Garden ecosystem health metrics"""
    overall_health_score: float = Field(..., ge=0, le=1, description="Overall garden health (0-1)")
    
    # Health indicators
    growth_momentum: float = Field(..., description="Current growth momentum")
    diversity_score: float = Field(..., description="Technology and project diversity")
    engagement_vitality: float = Field(..., description="Visitor engagement levels")
    maintenance_status: str = Field(..., description="Maintenance status")
    
    # Recommendations
    health_recommendations: List[str] = Field(..., description="Recommendations to improve health")
    at_risk_projects: List[str] = Field(..., description="Projects that need attention")
    growth_opportunities: List[str] = Field(..., description="Opportunities for growth")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "overall_health_score": 0.82,
                "growth_momentum": 1.15,
                "diversity_score": 0.78,
                "engagement_vitality": 0.91,
                "maintenance_status": "excellent",
                "health_recommendations": [
                    "Consider adding more backend projects to balance the garden",
                    "Some projects haven't received commits in 30+ days"
                ],
                "at_risk_projects": ["Old API Project"],
                "growth_opportunities": [
                    "High visitor engagement in AI/ML area - perfect for new projects",
                    "Spring season approaching - ideal for planting new seeds"
                ]
            }
        }
    )