"""
API v1 routes for Digital Greenhouse
"""

from fastapi import APIRouter
from .garden import router as garden_router
from .projects import router as projects_router
from .skills import router as skills_router
from .weather import router as weather_router
from .analytics import router as analytics_router
from .integrations import router as integrations_router
from .visitors import router as visitors_router

# Main API router
api_router = APIRouter(prefix="/api/v1")

# Include all route modules
api_router.include_router(
    garden_router,
    tags=["garden"],
    prefix="/garden"
)

api_router.include_router(
    projects_router,
    tags=["projects"],
    prefix="/projects"
)

api_router.include_router(
    skills_router,
    tags=["skills"],
    prefix="/skills"
)

api_router.include_router(
    weather_router,
    tags=["weather"],
    prefix="/weather"
)

api_router.include_router(
    analytics_router,
    tags=["analytics"],
    prefix="/analytics"
)

api_router.include_router(
    integrations_router,
    tags=["integrations"],
    prefix="/integrations"
)

api_router.include_router(
    visitors_router,
    tags=["visitors"],
    prefix="/visitors"
)