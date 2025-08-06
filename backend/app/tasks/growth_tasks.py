"""
Growth calculation and weather update tasks
"""

from celery import current_task
from sqlalchemy import select, and_
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
import logging

from app.tasks.celery_app import celery_app
from app.core.database import get_sync_db, SyncSessionLocal
from app.models.projects import Project, ProjectGrowthLog
from app.models.weather import WeatherState
from app.services.projects import ProjectService
from app.services.weather import WeatherService
from app.core.cache import cache_manager

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def calculate_project_growth(self, project_id: str) -> Dict[str, Any]:
    """
    Calculate growth for a specific project
    """
    try:
        with SyncSessionLocal() as db:
            # Get project
            result = db.execute(
                select(Project).where(Project.id == UUID(project_id))
            )
            project = result.scalar_one_or_none()
            
            if not project:
                logger.warning(f"Project not found: {project_id}")
                return {"success": False, "error": "Project not found"}
            
            # Calculate comprehensive growth metrics
            growth_metrics = _calculate_comprehensive_growth_metrics(project, db)
            
            # Determine new growth stage
            new_stage = _determine_growth_stage_from_metrics(project, growth_metrics)
            
            if new_stage != project.growth_stage:
                old_stage = project.growth_stage
                project.growth_stage = new_stage
                
                # Create growth log entry
                growth_log = ProjectGrowthLog(
                    project_id=project.id,
                    previous_stage=old_stage,
                    new_stage=new_stage,
                    commits_delta=growth_metrics.get('commits_delta', 0),
                    lines_added=growth_metrics.get('lines_added', 0),
                    lines_removed=growth_metrics.get('lines_removed', 0),
                    complexity_change=growth_metrics.get('complexity_change', 0),
                    github_activity=growth_metrics.get('github_activity'),
                    page_views=growth_metrics.get('page_views', 0),
                    interactions=growth_metrics.get('interactions', 0),
                    growth_factor=growth_metrics.get('growth_factor', 0),
                    recorded_at=datetime.utcnow()
                )
                
                db.add(growth_log)
                db.commit()
                
                logger.info(f"Growth stage changed: {project.name} from {old_stage} to {new_stage}")
                
                # Clear relevant caches asynchronously
                _clear_project_caches.delay(project_id)
                
                return {
                    "success": True,
                    "project_id": project_id,
                    "old_stage": old_stage,
                    "new_stage": new_stage,
                    "growth_factor": growth_metrics.get('growth_factor', 0)
                }
            
            return {
                "success": True,
                "project_id": project_id,
                "stage_unchanged": True,
                "current_stage": project.growth_stage
            }
    
    except Exception as exc:
        logger.error(f"Error calculating growth for project {project_id}: {exc}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            raise self.retry(countdown=countdown, exc=exc)
        
        return {"success": False, "error": str(exc)}


@celery_app.task(bind=True, max_retries=3)
def calculate_all_project_growth(self) -> Dict[str, Any]:
    """
    Calculate growth for all active projects
    """
    try:
        with SyncSessionLocal() as db:
            # Get all active projects
            result = db.execute(
                select(Project.id).where(Project.status == 'active')
            )
            project_ids = [str(pid) for pid in result.scalars().all()]
            
            # Schedule individual growth calculations
            results = []
            for project_id in project_ids:
                result = calculate_project_growth.delay(project_id)
                results.append(result.id)
            
            logger.info(f"Scheduled growth calculations for {len(project_ids)} projects")
            
            return {
                "success": True,
                "projects_scheduled": len(project_ids),
                "task_ids": results
            }
    
    except Exception as exc:
        logger.error(f"Error scheduling growth calculations: {exc}")
        
        if self.request.retries < self.max_retries:
            countdown = 60  # Wait 1 minute before retry
            raise self.retry(countdown=countdown, exc=exc)
        
        return {"success": False, "error": str(exc)}


@celery_app.task(bind=True, max_retries=3)
def update_weather_conditions(self) -> Dict[str, Any]:
    """
    Update garden weather conditions based on recent activity
    """
    try:
        with SyncSessionLocal() as db:
            # Gather activity data from last few hours
            cutoff_time = datetime.utcnow() - timedelta(hours=4)
            
            # Count recent GitHub activity (from growth logs)
            result = db.execute(
                select(
                    func.sum(ProjectGrowthLog.commits_delta),
                    func.avg(ProjectGrowthLog.complexity_change)
                )
                .where(ProjectGrowthLog.recorded_at >= cutoff_time)
            )
            activity_result = result.fetchone()
            recent_commits = activity_result[0] or 0
            avg_complexity_change = activity_result[1] or 0
            
            # Calculate coding hours (rough estimation from activity)
            coding_hours = min(recent_commits * 0.5, 8.0)  # Rough estimation
            
            # Get current music mood (would integrate with Spotify API)
            current_mood = _get_current_music_mood()
            
            # Get actual weather (would integrate with weather API)
            actual_weather = _get_actual_weather()
            
            # Create weather service and update conditions
            weather_service = WeatherService(db)
            
            updated_weather = weather_service.update_weather_conditions(
                github_commits=int(recent_commits),
                coding_hours=coding_hours,
                music_mood=current_mood,
                actual_weather=actual_weather
            )
            
            # Clear weather cache
            _clear_weather_caches.delay()
            
            logger.info(f"Weather updated: {updated_weather.weather_type} (intensity: {updated_weather.intensity})")
            
            return {
                "success": True,
                "weather_type": updated_weather.weather_type,
                "intensity": updated_weather.intensity,
                "factors": {
                    "recent_commits": recent_commits,
                    "coding_hours": coding_hours,
                    "music_mood": current_mood,
                    "actual_weather": actual_weather
                }
            }
    
    except Exception as exc:
        logger.error(f"Error updating weather conditions: {exc}")
        
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries * 60  # Exponential backoff in minutes
            raise self.retry(countdown=countdown, exc=exc)
        
        return {"success": False, "error": str(exc)}


@celery_app.task
def _clear_project_caches(project_id: str):
    """Clear caches related to a project"""
    try:
        # This would clear project-related caches
        # For now, just log
        logger.debug(f"Clearing caches for project: {project_id}")
    except Exception as e:
        logger.error(f"Error clearing project caches: {e}")


@celery_app.task 
def _clear_weather_caches():
    """Clear weather-related caches"""
    try:
        # This would clear weather caches
        # For now, just log
        logger.debug("Clearing weather caches")
    except Exception as e:
        logger.error(f"Error clearing weather caches: {e}")


# Helper functions
def _calculate_comprehensive_growth_metrics(project: Project, db) -> Dict[str, Any]:
    """Calculate comprehensive growth metrics for a project"""
    
    # Get recent growth logs to calculate deltas
    cutoff_time = datetime.utcnow() - timedelta(days=7)
    result = db.execute(
        select(ProjectGrowthLog)
        .where(
            and_(
                ProjectGrowthLog.project_id == project.id,
                ProjectGrowthLog.recorded_at >= cutoff_time
            )
        )
        .order_by(ProjectGrowthLog.recorded_at.desc())
        .limit(5)
    )
    recent_logs = result.scalars().all()
    
    # Calculate deltas
    commits_delta = sum(log.commits_delta or 0 for log in recent_logs)
    total_interactions = sum(log.interactions or 0 for log in recent_logs)
    
    # Calculate growth factor based on multiple metrics
    growth_factor = 0.0
    
    # Base activity factor
    if commits_delta > 0:
        growth_factor += min(commits_delta * 0.1, 0.4)
    
    # Interaction factor
    if total_interactions > 0:
        growth_factor += min(total_interactions * 0.02, 0.3)
    
    # Project age factor (newer projects grow faster)
    if project.planted_date:
        days_old = (datetime.utcnow() - project.planted_date).days
        if days_old < 30:
            growth_factor += 0.2
        elif days_old < 90:
            growth_factor += 0.1
    
    # Technology diversity factor
    tech_count = len(project.technologies or [])
    if tech_count >= 3:
        growth_factor += 0.1
    
    growth_factor = min(growth_factor, 1.0)
    
    return {
        "commits_delta": commits_delta,
        "lines_added": 0,  # Would get from GitHub API
        "lines_removed": 0,  # Would get from GitHub API
        "complexity_change": 0,  # Would calculate from code analysis
        "github_activity": {},  # Would populate from GitHub API
        "page_views": total_interactions,
        "interactions": total_interactions,
        "growth_factor": growth_factor
    }


def _determine_growth_stage_from_metrics(project: Project, metrics: Dict[str, Any]) -> str:
    """Determine growth stage based on comprehensive metrics"""
    
    growth_factor = metrics.get('growth_factor', 0)
    interactions = metrics.get('interactions', 0)
    commits = metrics.get('commits_delta', 0)
    
    # Growth stage thresholds
    if growth_factor >= 0.8 or interactions >= 50 or commits >= 20:
        return 'mature'
    elif growth_factor >= 0.6 or interactions >= 25 or commits >= 10:
        return 'blooming'
    elif growth_factor >= 0.4 or interactions >= 10 or commits >= 5:
        return 'growing'
    elif growth_factor >= 0.2 or interactions >= 5 or commits >= 1:
        return 'sprout'
    else:
        return 'seed'


def _get_current_music_mood() -> Optional[str]:
    """Get current music mood (placeholder for Spotify integration)"""
    # This would integrate with Spotify API
    return None


def _get_actual_weather() -> Optional[str]:
    """Get actual weather conditions (placeholder for weather API integration)"""
    # This would integrate with weather API
    return None