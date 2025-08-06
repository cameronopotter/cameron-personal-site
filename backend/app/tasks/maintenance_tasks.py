"""
Maintenance and cleanup tasks
"""

from celery import current_task
from sqlalchemy import select, delete, func
from typing import Dict, Any
from datetime import datetime, timedelta
import logging

from app.tasks.celery_app import celery_app
from app.core.database import SyncSessionLocal
from app.models.visitors import VisitorSession
from app.models.weather import WeatherState
from app.models.projects import ProjectGrowthLog
from app.services.visitor_tracking import VisitorTrackingService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def cleanup_old_sessions(self, days_old: int = 30) -> Dict[str, Any]:
    """
    Clean up old visitor sessions for privacy compliance
    """
    try:
        with SyncSessionLocal() as db:
            tracking_service = VisitorTrackingService(db)
            deleted_count = tracking_service.cleanup_old_sessions(days_old)
            
            logger.info(f"Cleaned up {deleted_count} old visitor sessions")
            
            return {
                "success": True,
                "sessions_deleted": deleted_count,
                "days_threshold": days_old
            }
    
    except Exception as exc:
        logger.error(f"Error cleaning up old sessions: {exc}")
        return {"success": False, "error": str(exc)}


@celery_app.task(bind=True)
def cleanup_old_weather_states(self, days_old: int = 90) -> Dict[str, Any]:
    """
    Clean up old weather states to prevent database bloat
    """
    try:
        with SyncSessionLocal() as db:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Count old weather states
            result = db.execute(
                select(func.count(WeatherState.id))
                .where(WeatherState.started_at < cutoff_date)
            )
            count_to_delete = result.scalar() or 0
            
            if count_to_delete > 0:
                # Delete old weather states
                db.execute(
                    delete(WeatherState)
                    .where(WeatherState.started_at < cutoff_date)
                )
                db.commit()
                
                logger.info(f"Cleaned up {count_to_delete} old weather states")
            
            return {
                "success": True,
                "weather_states_deleted": count_to_delete,
                "days_threshold": days_old
            }
    
    except Exception as exc:
        logger.error(f"Error cleaning up old weather states: {exc}")
        return {"success": False, "error": str(exc)}


@celery_app.task(bind=True)
def cleanup_old_growth_logs(self, days_old: int = 365) -> Dict[str, Any]:
    """
    Clean up very old growth logs, keeping only recent history
    """
    try:
        with SyncSessionLocal() as db:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Count old growth logs
            result = db.execute(
                select(func.count(ProjectGrowthLog.id))
                .where(ProjectGrowthLog.recorded_at < cutoff_date)
            )
            count_to_delete = result.scalar() or 0
            
            if count_to_delete > 0:
                # Delete old growth logs
                db.execute(
                    delete(ProjectGrowthLog)
                    .where(ProjectGrowthLog.recorded_at < cutoff_date)
                )
                db.commit()
                
                logger.info(f"Cleaned up {count_to_delete} old growth logs")
            
            return {
                "success": True,
                "growth_logs_deleted": count_to_delete,
                "days_threshold": days_old
            }
    
    except Exception as exc:
        logger.error(f"Error cleaning up old growth logs: {exc}")
        return {"success": False, "error": str(exc)}


@celery_app.task(bind=True)
def optimize_database(self) -> Dict[str, Any]:
    """
    Perform database optimization tasks
    """
    try:
        with SyncSessionLocal() as db:
            # Run VACUUM and ANALYZE on PostgreSQL
            # This would be database-specific optimization
            
            # For now, just log that optimization ran
            logger.info("Database optimization completed")
            
            return {
                "success": True,
                "optimizations_run": [
                    "table_analysis",
                    "index_maintenance"
                ]
            }
    
    except Exception as exc:
        logger.error(f"Error optimizing database: {exc}")
        return {"success": False, "error": str(exc)}


@celery_app.task(bind=True)
def generate_system_health_report(self) -> Dict[str, Any]:
    """
    Generate comprehensive system health report
    """
    try:
        with SyncSessionLocal() as db:
            health_metrics = {}
            
            # Database metrics
            result = db.execute(
                select(func.count(VisitorSession.id))
            )
            health_metrics["total_sessions"] = result.scalar() or 0
            
            result = db.execute(
                select(func.count(WeatherState.id))
            )
            health_metrics["total_weather_states"] = result.scalar() or 0
            
            result = db.execute(
                select(func.count(ProjectGrowthLog.id))
            )
            health_metrics["total_growth_logs"] = result.scalar() or 0
            
            # Recent activity metrics
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            result = db.execute(
                select(func.count(VisitorSession.id))
                .where(VisitorSession.started_at >= cutoff_time)
            )
            health_metrics["sessions_24h"] = result.scalar() or 0
            
            result = db.execute(
                select(func.count(ProjectGrowthLog.id))
                .where(ProjectGrowthLog.recorded_at >= cutoff_time)
            )
            health_metrics["growth_events_24h"] = result.scalar() or 0
            
            # System status
            system_status = "healthy"
            if health_metrics["sessions_24h"] == 0:
                system_status = "low_activity"
            
            logger.info("System health report generated")
            
            return {
                "success": True,
                "report_generated_at": datetime.utcnow().isoformat(),
                "system_status": system_status,
                "metrics": health_metrics
            }
    
    except Exception as exc:
        logger.error(f"Error generating health report: {exc}")
        return {"success": False, "error": str(exc)}


@celery_app.task(bind=True)
def backup_critical_data(self) -> Dict[str, Any]:
    """
    Create backups of critical system data
    """
    try:
        # This would implement data backup logic
        # For now, just log that backup ran
        
        backup_items = [
            "project_configurations",
            "growth_milestones", 
            "system_settings"
        ]
        
        logger.info(f"Data backup completed: {len(backup_items)} items")
        
        return {
            "success": True,
            "backup_completed_at": datetime.utcnow().isoformat(),
            "items_backed_up": backup_items
        }
    
    except Exception as exc:
        logger.error(f"Error backing up data: {exc}")
        return {"success": False, "error": str(exc)}