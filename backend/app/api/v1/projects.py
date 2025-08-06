"""
Project management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List
from uuid import UUID
import logging

from app.core.database import get_async_db
from app.core.cache import cache_manager, CacheKeys, CacheTTL
from app.models.projects import Project, ProjectGrowthLog
from app.schemas.base import PaginationParams, PaginatedResponse
from app.schemas.projects import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse,
    InteractionEvent, InteractionResponse, ProjectGrowthLogResponse
)
from app.services.projects import ProjectService
from app.services.visitor_tracking import get_or_create_visitor_session

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=PaginatedResponse)
async def list_projects(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = Query(None, description="Filter by project status"),
    growth_stage: Optional[str] = Query(None, description="Filter by growth stage"),
    technology: Optional[str] = Query(None, description="Filter by technology"),
    plant_type: Optional[str] = Query(None, description="Filter by plant type"),
    db: AsyncSession = Depends(get_async_db)
) -> PaginatedResponse:
    """
    List projects with filtering and pagination
    """
    try:
        project_service = ProjectService(db)
        
        # Build filters
        filters = {}
        if status:
            filters['status'] = status
        if growth_stage:
            filters['growth_stage'] = growth_stage
        if plant_type:
            filters['plant_type'] = plant_type
        if technology:
            filters['technology'] = technology
        
        # Get projects with pagination
        projects, total_count = await project_service.list_projects(
            filters=filters,
            pagination=pagination
        )
        
        # Convert to response models
        project_responses = [ProjectResponse.model_validate(p) for p in projects]
        
        return PaginatedResponse.create(
            items=project_responses,
            total_count=total_count,
            pagination=pagination
        )
    
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve projects")


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
) -> ProjectResponse:
    """
    Create a new project
    """
    try:
        project_service = ProjectService(db)
        
        # Create the project
        project = await project_service.create_project(project_data)
        
        # Schedule initial growth calculation
        background_tasks.add_task(
            project_service.trigger_growth_calculation,
            project.id
        )
        
        # Clear relevant caches
        await cache_manager.clear_pattern("garden:*")
        await cache_manager.clear_pattern("project:*")
        
        logger.info(f"Project created: {project.name} ({project.id})")
        return ProjectResponse.model_validate(project)
    
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail="Failed to create project")


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_details(
    project_id: UUID = Path(..., description="Project ID"),
    visitor_session: str = Depends(get_or_create_visitor_session),
    db: AsyncSession = Depends(get_async_db)
) -> ProjectDetailResponse:
    """
    Get detailed project information including growth history and analytics
    """
    try:
        cache_key = CacheKeys.project_details(str(project_id))
        
        # Try cache first
        cached_project = await cache_manager.get(cache_key)
        if cached_project:
            logger.debug(f"Project details served from cache: {project_id}")
            return ProjectDetailResponse(**cached_project)
        
        project_service = ProjectService(db)
        
        # Get project with details
        project_details = await project_service.get_project_details(
            project_id=project_id,
            visitor_session=visitor_session
        )
        
        if not project_details:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Cache the detailed response
        await cache_manager.set(
            cache_key,
            project_details.dict(),
            CacheTTL.PROJECT_DETAILS
        )
        
        logger.info(f"Project details served: {project_id}")
        return project_details
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project details {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve project")


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID = Path(..., description="Project ID"),
    project_data: ProjectUpdate = ...,
    background_tasks: BackgroundTasks = ...,
    db: AsyncSession = Depends(get_async_db)
) -> ProjectResponse:
    """
    Update project information
    """
    try:
        project_service = ProjectService(db)
        
        # Update the project
        updated_project = await project_service.update_project(
            project_id=project_id,
            project_data=project_data
        )
        
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Schedule growth recalculation if relevant fields changed
        background_tasks.add_task(
            project_service.trigger_growth_calculation,
            project_id
        )
        
        # Clear caches
        await cache_manager.delete(CacheKeys.project_details(str(project_id)))
        await cache_manager.clear_pattern("garden:*")
        
        logger.info(f"Project updated: {project_id}")
        return ProjectResponse.model_validate(updated_project)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update project")


@router.delete("/{project_id}")
async def delete_project(
    project_id: UUID = Path(..., description="Project ID"),
    db: AsyncSession = Depends(get_async_db)
) -> dict:
    """
    Delete a project
    """
    try:
        project_service = ProjectService(db)
        
        # Delete the project
        deleted = await project_service.delete_project(project_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Clear caches
        await cache_manager.delete(CacheKeys.project_details(str(project_id)))
        await cache_manager.clear_pattern("garden:*")
        
        logger.info(f"Project deleted: {project_id}")
        return {"success": True, "message": "Project deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete project")


@router.post("/{project_id}/interact", response_model=InteractionResponse)
async def record_project_interaction(
    project_id: UUID = Path(..., description="Project ID"),
    interaction: InteractionEvent = ...,
    background_tasks: BackgroundTasks = ...,
    visitor_session: str = Depends(get_or_create_visitor_session),
    db: AsyncSession = Depends(get_async_db)
) -> InteractionResponse:
    """
    Record visitor interaction with project
    Updates growth metrics and analytics
    Returns any triggered growth stage changes
    """
    try:
        project_service = ProjectService(db)
        
        # Record the interaction
        interaction_response = await project_service.record_interaction(
            project_id=project_id,
            interaction=interaction,
            visitor_session=visitor_session
        )
        
        # Schedule background updates if interaction was significant
        if interaction_response.growth_triggered:
            background_tasks.add_task(
                project_service.trigger_growth_calculation,
                project_id
            )
        
        # Update analytics in background
        background_tasks.add_task(
            project_service.update_interaction_analytics,
            project_id,
            interaction.interaction_type
        )
        
        logger.debug(f"Interaction recorded: {interaction.interaction_type} on {project_id}")
        return interaction_response
    
    except Exception as e:
        logger.error(f"Error recording interaction on {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to record interaction")


@router.get("/{project_id}/growth-history", response_model=List[ProjectGrowthLogResponse])
async def get_growth_history(
    project_id: UUID = Path(..., description="Project ID"),
    limit: int = Query(20, ge=1, le=100, description="Number of growth events to return"),
    db: AsyncSession = Depends(get_async_db)
) -> List[ProjectGrowthLogResponse]:
    """
    Get project growth history
    """
    try:
        # Check if project exists
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get growth history
        result = await db.execute(
            select(ProjectGrowthLog)
            .where(ProjectGrowthLog.project_id == project_id)
            .order_by(desc(ProjectGrowthLog.recorded_at))
            .limit(limit)
        )
        growth_logs = result.scalars().all()
        
        return [ProjectGrowthLogResponse.model_validate(log) for log in growth_logs]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting growth history for {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve growth history")


@router.post("/{project_id}/trigger-growth")
async def trigger_growth_calculation(
    project_id: UUID = Path(..., description="Project ID"),
    background_tasks: BackgroundTasks = ...,
    db: AsyncSession = Depends(get_async_db)
) -> dict:
    """
    Manually trigger growth calculation for a project
    """
    try:
        # Verify project exists
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_service = ProjectService(db)
        
        # Trigger growth calculation
        background_tasks.add_task(
            project_service.trigger_growth_calculation,
            project_id
        )
        
        logger.info(f"Growth calculation triggered for project: {project_id}")
        return {
            "success": True,
            "message": "Growth calculation triggered",
            "project_id": str(project_id)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering growth calculation for {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger growth calculation")


@router.get("/{project_id}/analytics")
async def get_project_analytics(
    project_id: UUID = Path(..., description="Project ID"),
    db: AsyncSession = Depends(get_async_db)
) -> dict:
    """
    Get analytics data for a specific project
    """
    try:
        cache_key = CacheKeys.project_analytics(str(project_id))
        
        # Try cache first
        cached_analytics = await cache_manager.get(cache_key)
        if cached_analytics:
            return cached_analytics
        
        project_service = ProjectService(db)
        analytics = await project_service.get_project_analytics(project_id)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Cache analytics
        await cache_manager.set(
            cache_key,
            analytics,
            CacheTTL.ANALYTICS_DASHBOARD
        )
        
        return analytics
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics for {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve project analytics")