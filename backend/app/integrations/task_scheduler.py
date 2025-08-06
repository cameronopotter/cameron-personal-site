"""
Background task orchestration and scheduling system.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from .github_service import GitHubService
from .spotify_service import SpotifyService  
from .weather_service import WeatherService
from .wakatime_service import WakaTimeService
from .social_service import SocialService
from .growth_engine import GrowthEngine
from .mood_engine import MoodEngine
from .analytics_processor import AnalyticsProcessor
from .cache_manager import cache_manager
from .websocket_manager import websocket_manager, WebSocketEvent, EventType
from .integration_config import integration_settings

import logging
logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(str, Enum):
    """Types of background tasks"""
    DATA_SYNC = "data_sync"
    ANALYTICS_PROCESSING = "analytics_processing"
    CACHE_MAINTENANCE = "cache_maintenance"
    MOOD_SYNTHESIS = "mood_synthesis"
    GROWTH_CALCULATION = "growth_calculation"
    HEALTH_CHECK = "health_check"
    CLEANUP = "cleanup"
    NOTIFICATION = "notification"


@dataclass
class TaskDefinition:
    """Background task definition"""
    task_id: str
    task_type: TaskType
    name: str
    description: str
    function: Callable
    priority: TaskPriority
    max_retries: int
    retry_delay_seconds: int
    timeout_seconds: int
    depends_on: List[str]  # Task IDs this task depends on
    metadata: Dict[str, Any]


@dataclass
class TaskExecution:
    """Task execution instance"""
    execution_id: str
    task_id: str
    status: TaskStatus
    scheduled_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    retry_count: int
    error_message: Optional[str]
    result: Optional[Any]
    context: Dict[str, Any]


@dataclass
class TaskSchedule:
    """Task scheduling configuration"""
    task_id: str
    cron_expression: Optional[str]  # Standard cron format
    interval_seconds: Optional[int]  # Simple interval
    next_run: datetime
    enabled: bool
    last_run: Optional[datetime]
    max_concurrent: int  # Max concurrent executions


class TaskScheduler:
    """Background task scheduler and orchestrator"""
    
    def __init__(self):
        # Service instances
        self.github_service = GitHubService()
        self.spotify_service = SpotifyService()
        self.weather_service = WeatherService()
        self.wakatime_service = WakaTimeService()
        self.social_service = SocialService()
        self.growth_engine = GrowthEngine()
        self.mood_engine = MoodEngine()
        self.analytics_processor = AnalyticsProcessor()
        
        # Task management
        self.task_definitions: Dict[str, TaskDefinition] = {}
        self.task_schedules: Dict[str, TaskSchedule] = {}
        self.executions: Dict[str, TaskExecution] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Scheduler state
        self.is_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        
        # Performance tracking
        self.stats = {
            "tasks_executed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0.0,
            "avg_execution_time": 0.0
        }
        
        # Initialize built-in tasks
        self._register_built_in_tasks()
    
    def _register_built_in_tasks(self):
        """Register built-in system tasks"""
        
        # GitHub data sync
        self.register_task(TaskDefinition(
            task_id="github_sync",
            task_type=TaskType.DATA_SYNC,
            name="GitHub Data Sync",
            description="Sync repository and commit data from GitHub",
            function=self._sync_github_data,
            priority=TaskPriority.NORMAL,
            max_retries=3,
            retry_delay_seconds=300,
            timeout_seconds=300,
            depends_on=[],
            metadata={"service": "github"}
        ))
        
        # Weather data sync
        self.register_task(TaskDefinition(
            task_id="weather_sync",
            task_type=TaskType.DATA_SYNC,
            name="Weather Data Sync",
            description="Sync current weather and forecast data",
            function=self._sync_weather_data,
            priority=TaskPriority.NORMAL,
            max_retries=2,
            retry_delay_seconds=60,
            timeout_seconds=60,
            depends_on=[],
            metadata={"service": "weather"}
        ))
        
        # Mood synthesis
        self.register_task(TaskDefinition(
            task_id="mood_synthesis",
            task_type=TaskType.MOOD_SYNTHESIS,
            name="Mood Synthesis",
            description="Synthesize current garden mood from all data sources",
            function=self._synthesize_mood,
            priority=TaskPriority.HIGH,
            max_retries=2,
            retry_delay_seconds=30,
            timeout_seconds=120,
            depends_on=["weather_sync"],  # Depends on weather data
            metadata={}
        ))
        
        # Growth calculation
        self.register_task(TaskDefinition(
            task_id="growth_calculation",
            task_type=TaskType.GROWTH_CALCULATION,
            name="Project Growth Calculation",
            description="Calculate project growth metrics and stages",
            function=self._calculate_growth_metrics,
            priority=TaskPriority.NORMAL,
            max_retries=2,
            retry_delay_seconds=120,
            timeout_seconds=300,
            depends_on=["github_sync"],
            metadata={}
        ))
        
        # Analytics processing
        self.register_task(TaskDefinition(
            task_id="analytics_processing",
            task_type=TaskType.ANALYTICS_PROCESSING,
            name="Analytics Processing",
            description="Process visitor analytics and generate insights",
            function=self._process_analytics,
            priority=TaskPriority.LOW,
            max_retries=1,
            retry_delay_seconds=300,
            timeout_seconds=180,
            depends_on=[],
            metadata={}
        ))
        
        # Cache maintenance
        self.register_task(TaskDefinition(
            task_id="cache_maintenance",
            task_type=TaskType.CACHE_MAINTENANCE,
            name="Cache Maintenance",
            description="Clean up expired cache entries and optimize performance",
            function=self._maintain_cache,
            priority=TaskPriority.LOW,
            max_retries=1,
            retry_delay_seconds=600,
            timeout_seconds=120,
            depends_on=[],
            metadata={}
        ))
        
        # Health checks
        self.register_task(TaskDefinition(
            task_id="health_checks",
            task_type=TaskType.HEALTH_CHECK,
            name="Integration Health Checks",
            description="Check health of all integration services",
            function=self._perform_health_checks,
            priority=TaskPriority.HIGH,
            max_retries=1,
            retry_delay_seconds=60,
            timeout_seconds=60,
            depends_on=[],
            metadata={}
        ))
        
        # Data cleanup
        self.register_task(TaskDefinition(
            task_id="data_cleanup",
            task_type=TaskType.CLEANUP,
            name="Data Cleanup",
            description="Clean up old data based on retention policies",
            function=self._cleanup_old_data,
            priority=TaskPriority.LOW,
            max_retries=1,
            retry_delay_seconds=3600,
            timeout_seconds=300,
            depends_on=[],
            metadata={}
        ))
    
    def register_task(self, task_definition: TaskDefinition):
        """Register a new task definition"""
        self.task_definitions[task_definition.task_id] = task_definition
        logger.info(f"Registered task: {task_definition.name} ({task_definition.task_id})")
    
    def schedule_task(
        self, 
        task_id: str, 
        cron_expression: Optional[str] = None,
        interval_seconds: Optional[int] = None,
        enabled: bool = True,
        max_concurrent: int = 1
    ):
        """Schedule a task for automatic execution"""
        
        if task_id not in self.task_definitions:
            raise ValueError(f"Task {task_id} not found")
        
        next_run = self._calculate_next_run(cron_expression, interval_seconds)
        
        schedule = TaskSchedule(
            task_id=task_id,
            cron_expression=cron_expression,
            interval_seconds=interval_seconds,
            next_run=next_run,
            enabled=enabled,
            last_run=None,
            max_concurrent=max_concurrent
        )
        
        self.task_schedules[task_id] = schedule
        logger.info(f"Scheduled task {task_id} - next run: {next_run}")
    
    def schedule_default_tasks(self):
        """Schedule default system tasks"""
        
        # Frequent tasks (every few minutes)
        self.schedule_task("mood_synthesis", interval_seconds=180)  # Every 3 minutes
        self.schedule_task("health_checks", interval_seconds=300)   # Every 5 minutes
        
        # Regular tasks (every 15-30 minutes)
        self.schedule_task("weather_sync", interval_seconds=900)    # Every 15 minutes
        self.schedule_task("github_sync", interval_seconds=1800)    # Every 30 minutes
        
        # Hourly tasks
        self.schedule_task("growth_calculation", interval_seconds=3600)  # Every hour
        self.schedule_task("analytics_processing", interval_seconds=3600) # Every hour
        
        # Daily tasks (using cron expressions)
        self.schedule_task("cache_maintenance", cron_expression="0 2 * * *")  # 2 AM daily
        self.schedule_task("data_cleanup", cron_expression="0 3 * * *")       # 3 AM daily
    
    async def start(self):
        """Start the task scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Task scheduler started")
    
    async def stop(self):
        """Stop the task scheduler"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel scheduler loop
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Cancel running tasks
        for task in self.running_tasks.values():
            task.cancel()
        
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
        
        logger.info("Task scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        
        while self.is_running:
            try:
                await self._check_scheduled_tasks()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_scheduled_tasks(self):
        """Check for tasks that need to be executed"""
        
        current_time = datetime.utcnow()
        
        for task_id, schedule in self.task_schedules.items():
            if not schedule.enabled:
                continue
            
            if current_time >= schedule.next_run:
                # Check if we can run this task (dependency and concurrency limits)
                if await self._can_execute_task(task_id, schedule):
                    await self._execute_task(task_id)
                    
                    # Update schedule
                    schedule.last_run = current_time
                    schedule.next_run = self._calculate_next_run(
                        schedule.cron_expression,
                        schedule.interval_seconds
                    )
    
    async def _can_execute_task(self, task_id: str, schedule: TaskSchedule) -> bool:
        """Check if a task can be executed"""
        
        task_definition = self.task_definitions[task_id]
        
        # Check dependencies
        for dependency_id in task_definition.depends_on:
            if not await self._is_dependency_satisfied(dependency_id):
                logger.debug(f"Task {task_id} waiting for dependency {dependency_id}")
                return False
        
        # Check concurrency limits
        running_count = sum(1 for exec_id, execution in self.executions.items() 
                          if execution.task_id == task_id and execution.status == TaskStatus.RUNNING)
        
        if running_count >= schedule.max_concurrent:
            logger.debug(f"Task {task_id} at max concurrency ({running_count}/{schedule.max_concurrent})")
            return False
        
        return True
    
    async def _is_dependency_satisfied(self, dependency_task_id: str) -> bool:
        """Check if a dependency task has completed successfully recently"""
        
        # Find the most recent successful execution of the dependency
        recent_executions = [
            execution for execution in self.executions.values()
            if (execution.task_id == dependency_task_id and 
                execution.status == TaskStatus.COMPLETED and
                execution.completed_at and
                (datetime.utcnow() - execution.completed_at).seconds < 3600)  # Within last hour
        ]
        
        return len(recent_executions) > 0
    
    async def execute_task_now(self, task_id: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Execute a task immediately"""
        return await self._execute_task(task_id, context)
    
    async def _execute_task(
        self, 
        task_id: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute a task"""
        
        if task_id not in self.task_definitions:
            raise ValueError(f"Task {task_id} not found")
        
        task_definition = self.task_definitions[task_id]
        execution_id = str(uuid.uuid4())
        
        # Create execution record
        execution = TaskExecution(
            execution_id=execution_id,
            task_id=task_id,
            status=TaskStatus.PENDING,
            scheduled_at=datetime.utcnow(),
            started_at=None,
            completed_at=None,
            duration_seconds=None,
            retry_count=0,
            error_message=None,
            result=None,
            context=context or {}
        )
        
        self.executions[execution_id] = execution
        
        # Start task execution
        task = asyncio.create_task(
            self._run_task_with_timeout(execution_id, task_definition)
        )
        self.running_tasks[execution_id] = task
        
        logger.info(f"Started task execution: {task_definition.name} ({execution_id})")
        return execution_id
    
    async def _run_task_with_timeout(
        self, 
        execution_id: str, 
        task_definition: TaskDefinition
    ):
        """Run task with timeout and error handling"""
        
        execution = self.executions[execution_id]
        
        try:
            execution.status = TaskStatus.RUNNING
            execution.started_at = datetime.utcnow()
            
            # Execute with timeout
            result = await asyncio.wait_for(
                task_definition.function(),
                timeout=task_definition.timeout_seconds
            )
            
            # Task completed successfully
            execution.status = TaskStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
            execution.result = result
            
            # Update stats
            self.stats["tasks_executed"] += 1
            self.stats["total_execution_time"] += execution.duration_seconds
            self.stats["avg_execution_time"] = (
                self.stats["total_execution_time"] / self.stats["tasks_executed"]
            )
            
            logger.info(
                f"Task completed: {task_definition.name} "
                f"({execution_id}) in {execution.duration_seconds:.2f}s"
            )
            
        except asyncio.TimeoutError:
            execution.status = TaskStatus.FAILED
            execution.error_message = f"Task timed out after {task_definition.timeout_seconds}s"
            execution.completed_at = datetime.utcnow()
            
            self.stats["tasks_failed"] += 1
            logger.error(f"Task timeout: {task_definition.name} ({execution_id})")
            
            # Schedule retry if allowed
            await self._schedule_retry(execution_id, task_definition)
            
        except Exception as e:
            execution.status = TaskStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            
            self.stats["tasks_failed"] += 1
            logger.error(f"Task failed: {task_definition.name} ({execution_id}): {e}")
            
            # Schedule retry if allowed
            await self._schedule_retry(execution_id, task_definition)
            
        finally:
            # Clean up running task reference
            if execution_id in self.running_tasks:
                del self.running_tasks[execution_id]
    
    async def _schedule_retry(self, execution_id: str, task_definition: TaskDefinition):
        """Schedule a task retry if retries are available"""
        
        execution = self.executions[execution_id]
        
        if execution.retry_count < task_definition.max_retries:
            execution.retry_count += 1
            execution.status = TaskStatus.RETRYING
            
            logger.info(
                f"Scheduling retry {execution.retry_count}/{task_definition.max_retries} "
                f"for task {task_definition.name} in {task_definition.retry_delay_seconds}s"
            )
            
            # Schedule retry
            asyncio.create_task(
                self._delayed_retry(execution_id, task_definition.retry_delay_seconds)
            )
        else:
            logger.error(
                f"Task {task_definition.name} ({execution_id}) exhausted all retries"
            )
    
    async def _delayed_retry(self, execution_id: str, delay_seconds: int):
        """Execute a delayed retry"""
        
        await asyncio.sleep(delay_seconds)
        
        execution = self.executions[execution_id]
        task_definition = self.task_definitions[execution.task_id]
        
        # Reset execution state for retry
        execution.status = TaskStatus.PENDING
        execution.started_at = None
        execution.completed_at = None
        execution.error_message = None
        
        # Start new execution
        task = asyncio.create_task(
            self._run_task_with_timeout(execution_id, task_definition)
        )
        self.running_tasks[execution_id] = task
    
    def _calculate_next_run(
        self, 
        cron_expression: Optional[str], 
        interval_seconds: Optional[int]
    ) -> datetime:
        """Calculate next execution time"""
        
        current_time = datetime.utcnow()
        
        if interval_seconds:
            return current_time + timedelta(seconds=interval_seconds)
        
        if cron_expression:
            # Simple cron parsing (would use croniter in production)
            # For now, just handle daily at specific hour
            if cron_expression.startswith("0 "):
                try:
                    hour = int(cron_expression.split()[1])
                    next_run = current_time.replace(hour=hour, minute=0, second=0, microsecond=0)
                    if next_run <= current_time:
                        next_run += timedelta(days=1)
                    return next_run
                except:
                    pass
        
        # Default: run in 1 hour
        return current_time + timedelta(hours=1)
    
    # Built-in task functions
    
    async def _sync_github_data(self) -> Dict[str, Any]:
        """Sync GitHub repository and activity data"""
        
        if not self.github_service.is_available():
            raise Exception("GitHub service not available")
        
        # Get activity summary
        activity_response = await self.github_service.get_user_activity_summary(30)
        if not activity_response.success:
            raise Exception(f"Failed to sync GitHub data: {activity_response.error}")
        
        activity = activity_response.data
        
        # Cache the activity data
        await cache_manager.set(
            "github:activity_summary",
            {
                "commits_today": activity.commits_today,
                "commits_this_week": activity.commits_this_week, 
                "repositories_updated": activity.repositories_updated,
                "last_activity": activity.last_activity.isoformat() if activity.last_activity else None
            },
            ttl_seconds=1800
        )
        
        # Broadcast activity update
        await websocket_manager.broadcast_event(WebSocketEvent(
            type=EventType.COMMIT_PUSHED,
            data={
                "commits_today": activity.commits_today,
                "active_repositories": len(activity.repositories_updated)
            },
            timestamp=datetime.utcnow(),
            source="github_sync"
        ))
        
        return {"repositories_synced": len(activity.repositories_updated)}
    
    async def _sync_weather_data(self) -> Dict[str, Any]:
        """Sync weather data"""
        
        if not self.weather_service.is_available():
            raise Exception("Weather service not available")
        
        # Get comprehensive weather data
        weather_data = await self.weather_service.get_comprehensive_weather_data()
        
        if "error" in weather_data:
            raise Exception(f"Failed to sync weather data: {weather_data['error']}")
        
        # Cache weather data
        await cache_manager.set("weather:current", weather_data, ttl_seconds=900)
        
        # Broadcast weather update
        await websocket_manager.broadcast_event(WebSocketEvent(
            type=EventType.WEATHER_UPDATED,
            data=weather_data["current"],
            timestamp=datetime.utcnow(),
            source="weather_sync"
        ))
        
        return {"condition": weather_data["current"]["condition"]}
    
    async def _synthesize_mood(self) -> Dict[str, Any]:
        """Synthesize garden mood"""
        
        mood = await self.mood_engine.synthesize_current_mood()
        
        # Cache mood data
        await cache_manager.set(
            "mood:current",
            {
                "atmosphere": mood.primary_atmosphere.value,
                "weather_pattern": mood.weather_pattern.value,
                "energy_level": mood.energy_level,
                "data_sources": mood.data_sources
            },
            ttl_seconds=300
        )
        
        return {
            "atmosphere": mood.primary_atmosphere.value,
            "confidence": mood.confidence
        }
    
    async def _calculate_growth_metrics(self) -> Dict[str, Any]:
        """Calculate project growth metrics"""
        
        portfolio = await self.growth_engine.get_portfolio_overview()
        
        if "error" in portfolio:
            raise Exception(f"Failed to calculate growth: {portfolio['error']}")
        
        # Cache growth data
        await cache_manager.set("growth:portfolio", portfolio, ttl_seconds=3600)
        
        return {
            "projects_analyzed": portfolio["total_projects"],
            "avg_growth": portfolio["avg_growth_score"]
        }
    
    async def _process_analytics(self) -> Dict[str, Any]:
        """Process visitor analytics"""
        
        metrics = self.analytics_processor.get_engagement_metrics(24)
        
        # Cache analytics
        await cache_manager.set("analytics:metrics_24h", asdict(metrics), ttl_seconds=3600)
        
        return {
            "unique_visitors": metrics.unique_visitors_24h,
            "avg_session_duration": metrics.avg_session_duration
        }
    
    async def _maintain_cache(self) -> Dict[str, Any]:
        """Perform cache maintenance"""
        
        expired_count = await cache_manager.cleanup_expired_entries()
        
        return {"expired_entries_cleaned": expired_count}
    
    async def _perform_health_checks(self) -> Dict[str, Any]:
        """Perform health checks on all services"""
        
        health_results = {}
        
        services = [
            ("github", self.github_service),
            ("spotify", self.spotify_service),
            ("weather", self.weather_service),
            ("wakatime", self.wakatime_service),
            ("social", self.social_service)
        ]
        
        for service_name, service in services:
            try:
                is_healthy = await service.health_check()
                health_results[service_name] = "healthy" if is_healthy else "unhealthy"
            except Exception as e:
                health_results[service_name] = f"error: {str(e)}"
        
        return health_results
    
    async def _cleanup_old_data(self) -> Dict[str, Any]:
        """Clean up old data"""
        
        retention_days = integration_settings.privacy.data_retention_days
        
        # Clean up analytics data
        await self.analytics_processor.cleanup_old_data(retention_days)
        
        # Clean up old task executions (keep last 1000)
        if len(self.executions) > 1000:
            sorted_executions = sorted(
                self.executions.items(),
                key=lambda x: x[1].scheduled_at,
                reverse=True
            )
            
            # Keep the 1000 most recent
            self.executions = dict(sorted_executions[:1000])
        
        return {"retention_days": retention_days}
    
    def get_task_status(self, execution_id: str) -> Optional[TaskExecution]:
        """Get status of a task execution"""
        return self.executions.get(execution_id)
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        
        running_count = len(self.running_tasks)
        recent_executions = [
            e for e in self.executions.values()
            if e.completed_at and (datetime.utcnow() - e.completed_at).seconds < 3600
        ]
        
        return {
            "is_running": self.is_running,
            "registered_tasks": len(self.task_definitions),
            "scheduled_tasks": len(self.task_schedules),
            "running_tasks": running_count,
            "recent_executions": len(recent_executions),
            "total_executions": len(self.executions),
            "stats": self.stats
        }


# Global task scheduler instance
task_scheduler = TaskScheduler()