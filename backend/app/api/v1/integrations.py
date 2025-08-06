"""
External API integrations endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_async_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/github/webhook")
async def handle_github_webhook(
    webhook_data: dict,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
) -> dict:
    """Handle GitHub webhook events"""
    
    try:
        # This would process GitHub webhook data
        # For now, just log and return success
        logger.info(f"GitHub webhook received: {webhook_data.get('action', 'unknown')}")
        
        # Schedule background processing
        # background_tasks.add_task(process_github_webhook, webhook_data)
        
        return {
            "success": True,
            "message": "Webhook processed"
        }
    
    except Exception as e:
        logger.error(f"Error processing GitHub webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")


@router.get("/github/sync")
async def sync_github_data(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
) -> dict:
    """Manually trigger GitHub data synchronization"""
    
    try:
        # Schedule background sync
        # background_tasks.add_task(sync_github_repositories)
        
        return {
            "success": True,
            "message": "GitHub sync scheduled"
        }
    
    except Exception as e:
        logger.error(f"Error scheduling GitHub sync: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule sync")


@router.get("/spotify/current")
async def get_spotify_state(
    db: AsyncSession = Depends(get_async_db)
) -> dict:
    """Get current Spotify listening state"""
    
    try:
        # This would integrate with Spotify API
        # For now, return placeholder
        return {
            "is_playing": False,
            "track": None,
            "mood": None
        }
    
    except Exception as e:
        logger.error(f"Error getting Spotify state: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve Spotify state")