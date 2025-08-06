"""
Visitor tracking and analytics API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from app.core.database import get_async_db
from app.schemas.visitors import (
    VisitorSessionResponse, SessionCreateRequest, VisitorAnalytics
)
from app.services.visitor_tracking import (
    VisitorTrackingService, get_or_create_visitor_session
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/session")
async def create_session(
    request: Request,
    session_data: SessionCreateRequest,
    db: AsyncSession = Depends(get_async_db)
) -> dict:
    """Create a new visitor session"""
    
    try:
        session_token = await get_or_create_visitor_session(request, db)
        return {
            "success": True,
            "session_token": session_token,
            "message": "Session created successfully"
        }
    
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.get("/analytics", response_model=VisitorAnalytics)
async def get_visitor_analytics(
    hours_back: int = 24,
    db: AsyncSession = Depends(get_async_db)
) -> VisitorAnalytics:
    """Get visitor analytics summary"""
    
    try:
        tracking_service = VisitorTrackingService(db)
        analytics = await tracking_service.get_visitor_analytics_summary(hours_back)
        
        # Convert to VisitorAnalytics model
        return VisitorAnalytics(
            total_sessions=analytics["total_sessions"],
            active_sessions=analytics["active_sessions"],
            average_session_duration=0.0,  # Placeholder
            average_engagement_score=analytics["average_engagement_score"],
            device_breakdown=analytics["device_breakdown"],
            browser_breakdown={},  # Placeholder
            country_breakdown={},  # Placeholder
            most_viewed_projects=analytics["popular_projects"],
            common_journey_paths=[],  # Placeholder
            interaction_heatmap={},  # Placeholder
            hourly_activity=[],  # Placeholder
            daily_trends=[]  # Placeholder
        )
    
    except Exception as e:
        logger.error(f"Error getting visitor analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")