"""
Simple asyncio-based background task system for Digital Greenhouse API
Replaces Celery with lightweight in-process task scheduling
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from enum import Enum

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.integrations.growth_engine import GrowthEngine
from app.integrations.weather_service import WeatherService
from app.integrations.github_service import GitHubService

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskResult:
    """Task execution result"""
    task_name: str
    status: TaskStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_seconds: Optional[float] = None


class BackgroundTaskManager:
    """Simple background task manager using asyncio"""
    
    def __init__(self):
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_results: Dict[str, TaskResult] = {}
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}
        self._shutdown_event = asyncio.Event()
        
    async def start(self):
        """Start the background task manager"""
        logger.info("Starting background task manager...")
        
        if not settings.enable_background_tasks:
            logger.info("Background tasks disabled in configuration")
            return
        
        # Schedule recurring tasks
        self._schedule_recurring_tasks()
        
        # Start the task scheduler loop
        asyncio.create_task(self._scheduler_loop())
        
        logger.info("Background task manager started")
    
    async def stop(self):
        """Stop the background task manager"""
        logger.info("Stopping background task manager...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel all running tasks
        for task_name, task in self.running_tasks.items():
            if not task.done():
                logger.info(f"Cancelling task: {task_name}")
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.running_tasks.clear()
        logger.info("Background task manager stopped")
    
    def _schedule_recurring_tasks(self):
        """Schedule recurring background tasks"""
        config = settings.background_tasks_config
        
        # Growth calculation task
        self.scheduled_tasks["calculate_growth"] = {
            "func": self._calculate_project_growth,
            "interval": config["growth_calculation_interval"],
            "last_run": None
        }
        
        # Weather update task
        self.scheduled_tasks["update_weather"] = {
            "func": self._update_weather_conditions,
            "interval": config["weather_update_interval"],
            "last_run": None
        }
        
        # Data sync task
        self.scheduled_tasks["sync_external_data"] = {
            "func": self._sync_external_data,
            "interval": config["data_sync_interval"],
            "last_run": None
        }
    
    async def _scheduler_loop(self):
        """Main scheduler loop that runs recurring tasks"""
        while not self._shutdown_event.is_set():
            try:
                current_time = datetime.now()
                
                for task_name, task_config in self.scheduled_tasks.items():
                    # Check if task needs to run
                    last_run = task_config.get("last_run")
                    interval = task_config["interval"]
                    
                    should_run = (
                        last_run is None or  # Never run before
                        (current_time - last_run).total_seconds() >= interval
                    )
                    
                    if should_run and task_name not in self.running_tasks:
                        logger.info(f"Starting scheduled task: {task_name}")
                        await self.execute_task(task_name, task_config["func"])
                        task_config["last_run"] = current_time
                
                # Sleep for 30 seconds before checking again
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def execute_task(self, task_name: str, task_func: Callable, *args, **kwargs) -> TaskResult:
        """Execute a background task"""
        if task_name in self.running_tasks:
            logger.warning(f"Task {task_name} is already running")
            return self.task_results.get(task_name)
        
        # Create task result
        result = TaskResult(
            task_name=task_name,
            status=TaskStatus.PENDING,
            started_at=datetime.now()
        )
        self.task_results[task_name] = result
        
        # Execute task
        task = asyncio.create_task(self._execute_task_wrapper(task_name, task_func, *args, **kwargs))
        self.running_tasks[task_name] = task
        
        return result
    
    async def _execute_task_wrapper(self, task_name: str, task_func: Callable, *args, **kwargs):
        """Wrapper for task execution with error handling and result tracking"""
        result = self.task_results[task_name]
        result.status = TaskStatus.RUNNING
        
        try:
            logger.info(f"Executing task: {task_name}")
            
            # Execute the task
            task_result = await task_func(*args, **kwargs)
            
            # Update result
            result.status = TaskStatus.COMPLETED
            result.completed_at = datetime.now()
            result.result = task_result
            result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
            
            logger.info(f"Task completed successfully: {task_name} (duration: {result.duration_seconds:.2f}s)")
            
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.completed_at = datetime.now()
            result.error = str(e)
            result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
            
            logger.error(f"Task failed: {task_name} - {e}")
        
        finally:
            # Remove from running tasks
            self.running_tasks.pop(task_name, None)
    
    async def get_task_status(self, task_name: str) -> Optional[TaskResult]:
        """Get status of a specific task"""
        return self.task_results.get(task_name)
    
    async def get_all_task_statuses(self) -> Dict[str, TaskResult]:
        """Get status of all tasks"""
        return self.task_results.copy()
    
    async def _calculate_project_growth(self) -> Dict[str, Any]:
        """Calculate growth for all projects"""
        async with AsyncSessionLocal() as session:
            growth_engine = GrowthEngine(session)
            
            # Calculate growth for all active projects
            results = await growth_engine.calculate_all_project_growth()
            
            logger.info(f"Growth calculation completed for {len(results)} projects")
            return {
                "projects_updated": len(results),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _update_weather_conditions(self) -> Dict[str, Any]:
        """Update weather conditions based on various factors"""
        async with AsyncSessionLocal() as session:
            weather_service = WeatherService(session)
            
            # Update weather based on activity, mood, time, etc.
            new_weather = await weather_service.calculate_new_weather_state()
            
            if new_weather:
                logger.info(f"Weather updated to: {new_weather.weather_type}")
                return {
                    "weather_type": new_weather.weather_type.value,
                    "temperature": new_weather.temperature,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.info("Weather conditions remain unchanged")
                return {
                    "unchanged": True,
                    "timestamp": datetime.now().isoformat()
                }
    
    async def _sync_external_data(self) -> Dict[str, Any]:
        """Sync data from external APIs (GitHub, etc.)"""
        results = {
            "github": {"synced": False, "error": None},
            "timestamp": datetime.now().isoformat()
        }
        
        if settings.enable_github_integration and settings.github_token:
            try:
                async with AsyncSessionLocal() as session:
                    github_service = GitHubService(session)
                    sync_result = await github_service.sync_all_repositories()
                    
                    results["github"] = {
                        "synced": True,
                        "repositories": len(sync_result.get("repositories", [])),
                        "updated_projects": sync_result.get("updated_projects", 0)
                    }
                    logger.info(f"GitHub sync completed: {sync_result}")
                    
            except Exception as e:
                results["github"]["error"] = str(e)
                logger.error(f"GitHub sync failed: {e}")
        
        return results


# Global task manager instance
task_manager = BackgroundTaskManager()


async def start_background_tasks():
    """Start background task system"""
    await task_manager.start()


async def stop_background_tasks():
    """Stop background task system"""
    await task_manager.stop()


async def execute_growth_calculation() -> TaskResult:
    """Manually trigger growth calculation"""
    return await task_manager.execute_task("manual_growth_calculation", task_manager._calculate_project_growth)


async def execute_weather_update() -> TaskResult:
    """Manually trigger weather update"""
    return await task_manager.execute_task("manual_weather_update", task_manager._update_weather_conditions)


async def execute_data_sync() -> TaskResult:
    """Manually trigger data sync"""
    return await task_manager.execute_task("manual_data_sync", task_manager._sync_external_data)


async def get_task_status(task_name: str) -> Optional[TaskResult]:
    """Get status of a specific task"""
    return await task_manager.get_task_status(task_name)


async def get_all_tasks_status() -> Dict[str, TaskResult]:
    """Get status of all tasks"""
    return await task_manager.get_all_task_statuses()