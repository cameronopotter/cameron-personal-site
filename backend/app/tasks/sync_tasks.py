"""
External data synchronization tasks
"""

from celery import current_task
from sqlalchemy import select, func
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from app.tasks.celery_app import celery_app
from app.core.database import SyncSessionLocal
from app.models.projects import Project, ProjectGrowthLog
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def sync_external_data(self) -> Dict[str, Any]:
    """
    Synchronize data from all external APIs
    """
    try:
        results = {}
        
        # Schedule individual sync tasks
        if settings.enable_github_integration:
            github_result = sync_github_data.delay()
            results["github_task_id"] = github_result.id
        
        if settings.enable_spotify_integration:
            spotify_result = sync_spotify_data.delay()
            results["spotify_task_id"] = spotify_result.id
        
        if settings.enable_weather_integration:
            weather_result = sync_weather_data.delay()
            results["weather_task_id"] = weather_result.id
        
        logger.info(f"External data sync scheduled: {len(results)} services")
        
        return {
            "success": True,
            "services_synced": len(results),
            "task_results": results
        }
    
    except Exception as exc:
        logger.error(f"Error scheduling external data sync: {exc}")
        
        if self.request.retries < self.max_retries:
            countdown = 300  # Wait 5 minutes before retry
            raise self.retry(countdown=countdown, exc=exc)
        
        return {"success": False, "error": str(exc)}


@celery_app.task(bind=True, max_retries=3)
def sync_github_data(self) -> Dict[str, Any]:
    """
    Synchronize GitHub repository data
    """
    try:
        if not settings.github_token:
            logger.warning("GitHub token not configured, skipping sync")
            return {"success": False, "error": "GitHub token not configured"}
        
        synced_repos = []
        
        with SyncSessionLocal() as db:
            # Get projects with GitHub repositories
            result = db.execute(
                select(Project).where(
                    Project.github_repo.isnot(None),
                    Project.status == 'active'
                )
            )
            projects = result.scalars().all()
            
            for project in projects:
                try:
                    repo_data = _fetch_github_repo_data(project.github_repo)
                    if repo_data:
                        _update_project_from_github(project, repo_data, db)
                        synced_repos.append({
                            "project_id": str(project.id),
                            "repo": project.github_repo,
                            "commits": repo_data.get("commit_count", 0)
                        })
                
                except Exception as e:
                    logger.error(f"Error syncing repo {project.github_repo}: {e}")
                    continue
            
            db.commit()
        
        logger.info(f"GitHub sync completed: {len(synced_repos)} repositories")
        
        return {
            "success": True,
            "repositories_synced": len(synced_repos),
            "synced_repos": synced_repos
        }
    
    except Exception as exc:
        logger.error(f"Error syncing GitHub data: {exc}")
        
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries * 300  # Exponential backoff
            raise self.retry(countdown=countdown, exc=exc)
        
        return {"success": False, "error": str(exc)}


@celery_app.task(bind=True, max_retries=3)
def sync_spotify_data(self) -> Dict[str, Any]:
    """
    Synchronize Spotify listening data
    """
    try:
        if not settings.spotify_client_id or not settings.spotify_client_secret:
            logger.warning("Spotify credentials not configured, skipping sync")
            return {"success": False, "error": "Spotify credentials not configured"}
        
        # This would integrate with Spotify API
        # For now, return placeholder
        
        logger.info("Spotify sync completed")
        
        return {
            "success": True,
            "current_track": None,
            "recent_listening": [],
            "mood_analysis": None
        }
    
    except Exception as exc:
        logger.error(f"Error syncing Spotify data: {exc}")
        
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries * 60
            raise self.retry(countdown=countdown, exc=exc)
        
        return {"success": False, "error": str(exc)}


@celery_app.task(bind=True, max_retries=3)
def sync_weather_data(self) -> Dict[str, Any]:
    """
    Synchronize external weather data
    """
    try:
        if not settings.weather_api_key:
            logger.warning("Weather API key not configured, skipping sync")
            return {"success": False, "error": "Weather API key not configured"}
        
        # This would integrate with weather API
        # For now, return placeholder
        
        weather_data = {
            "condition": "clear",
            "temperature": 22,
            "humidity": 65,
            "description": "Clear sky"
        }
        
        logger.info("Weather sync completed")
        
        return {
            "success": True,
            "weather_data": weather_data
        }
    
    except Exception as exc:
        logger.error(f"Error syncing weather data: {exc}")
        
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries * 60
            raise self.retry(countdown=countdown, exc=exc)
        
        return {"success": False, "error": str(exc)}


@celery_app.task(bind=True)
def sync_wakatime_data(self) -> Dict[str, Any]:
    """
    Synchronize WakaTime coding statistics
    """
    try:
        if not settings.wakatime_api_key:
            logger.warning("WakaTime API key not configured, skipping sync")
            return {"success": False, "error": "WakaTime API key not configured"}
        
        # This would integrate with WakaTime API
        # For now, return placeholder
        
        logger.info("WakaTime sync completed")
        
        return {
            "success": True,
            "total_seconds": 0,
            "languages": [],
            "projects": []
        }
    
    except Exception as exc:
        logger.error(f"Error syncing WakaTime data: {exc}")
        return {"success": False, "error": str(exc)}


# Helper functions
def _fetch_github_repo_data(repo_url: str) -> Dict[str, Any]:
    """
    Fetch repository data from GitHub API
    """
    try:
        # This would implement actual GitHub API calls
        # For now, return placeholder data
        
        return {
            "commit_count": 10,
            "contributors": 1,
            "stars": 5,
            "forks": 2,
            "issues": 3,
            "pull_requests": 1,
            "languages": {"Python": 70, "JavaScript": 30},
            "last_commit_date": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error fetching GitHub repo data for {repo_url}: {e}")
        return {}


def _update_project_from_github(project: Project, repo_data: Dict[str, Any], db) -> bool:
    """
    Update project with GitHub repository data
    """
    try:
        # Update project metrics
        old_commit_count = project.commit_count
        new_commit_count = repo_data.get("commit_count", 0)
        
        if new_commit_count > old_commit_count:
            project.commit_count = new_commit_count
            project.updated_at = datetime.utcnow()
            
            # Create growth log entry for the new commits
            growth_log = ProjectGrowthLog(
                project_id=project.id,
                commits_delta=new_commit_count - old_commit_count,
                github_activity=repo_data,
                recorded_at=datetime.utcnow()
            )
            
            db.add(growth_log)
            
            logger.info(f"Updated project {project.name}: {new_commit_count - old_commit_count} new commits")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error updating project {project.name} from GitHub: {e}")
        return False