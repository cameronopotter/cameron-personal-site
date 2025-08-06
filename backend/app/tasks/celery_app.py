"""
Celery application configuration
"""

from celery import Celery
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "digital_greenhouse",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.growth_tasks",
        "app.tasks.sync_tasks", 
        "app.tasks.maintenance_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # 1 hour
    task_routes={
        "app.tasks.growth_tasks.*": {"queue": "growth"},
        "app.tasks.sync_tasks.*": {"queue": "sync"},
        "app.tasks.maintenance_tasks.*": {"queue": "maintenance"}
    },
    beat_schedule={
        "calculate-project-growth": {
            "task": "app.tasks.growth_tasks.calculate_all_project_growth",
            "schedule": settings.growth_calculation_interval_minutes * 60,
        },
        "update-weather": {
            "task": "app.tasks.growth_tasks.update_weather_conditions",
            "schedule": settings.weather_update_interval_minutes * 60,
        },
        "sync-github-data": {
            "task": "app.tasks.sync_tasks.sync_github_data",
            "schedule": settings.data_sync_interval_hours * 3600,
        },
        "cleanup-sessions": {
            "task": "app.tasks.maintenance_tasks.cleanup_old_sessions",
            "schedule": 24 * 3600,  # Daily
        }
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=100
)

# Task error handling
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    logger.info(f'Request: {self.request!r}')
    return "Debug task completed"