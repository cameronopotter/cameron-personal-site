"""
Pydantic schemas for request/response validation
"""

from .base import *
from .projects import *
from .skills import *
from .weather import *
from .visitors import *
from .garden import *
from .analytics import *

__all__ = [
    # Base schemas
    "BaseResponse",
    "ErrorResponse", 
    "SuccessResponse",
    "Position3D",
    
    # Project schemas
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate", 
    "ProjectResponse",
    "ProjectDetailResponse",
    "ProjectGrowthLogResponse",
    "SeedPlantingRequest",
    "PlantedSeedResponse",
    
    # Skill schemas
    "SkillBase",
    "SkillCreate",
    "SkillUpdate",
    "SkillResponse",
    "SkillConnectionResponse",
    
    # Weather schemas  
    "WeatherStateResponse",
    "WeatherUpdateResponse",
    "MoodUpdateRequest",
    
    # Visitor schemas
    "VisitorSessionResponse",
    "InteractionEvent", 
    "InteractionResponse",
    
    # Garden schemas
    "GardenState",
    "GardenSummaryResponse",
    
    # Analytics schemas
    "AnalyticsDashboard",
    "RealtimeMetrics",
    "EngagementMetrics"
]