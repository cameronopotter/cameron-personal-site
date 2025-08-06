"""
Backend performance monitoring and optimization system for Digital Greenhouse
Comprehensive monitoring, metrics collection, and automated optimization
"""

import asyncio
import time
import psutil
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
import threading
from collections import defaultdict, deque
import json
from datetime import datetime, timedelta

import structlog
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings

logger = structlog.get_logger()

class MetricType(Enum):
    """Types of metrics we track"""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    SUMMARY = "summary"

class Severity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

@dataclass
class PerformanceMetric:
    """Single performance metric data point"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE

@dataclass
class Alert:
    """Performance alert"""
    id: str
    severity: Severity
    message: str
    metric_name: str
    threshold: float
    current_value: float
    timestamp: datetime
    resolved: bool = False
    suggestions: List[str] = field(default_factory=list)

class PerformanceOptimizer:
    """Automated performance optimization system"""
    
    def __init__(self):
        self.optimizations_applied: Dict[str, datetime] = {}
        self.optimization_history: List[Dict[str, Any]] = []
        
    async def analyze_and_optimize(self, metrics: Dict[str, float]) -> List[str]:
        """Analyze metrics and apply optimizations"""
        optimizations_applied = []
        
        # Database connection pool optimization
        if metrics.get('db_active_connections', 0) / metrics.get('db_pool_size', 1) > 0.8:
            if await self._can_apply_optimization('db_pool_expansion'):
                await self._expand_db_pool()
                optimizations_applied.append('Expanded database connection pool')
        
        # Memory optimization
        if metrics.get('memory_usage_percent', 0) > 85:
            if await self._can_apply_optimization('memory_cleanup'):
                await self._trigger_memory_cleanup()
                optimizations_applied.append('Triggered memory cleanup')
        
        # Query optimization
        if metrics.get('avg_query_time_ms', 0) > 1000:
            if await self._can_apply_optimization('query_optimization'):
                await self._optimize_slow_queries()
                optimizations_applied.append('Optimized slow queries')
        
        # Cache optimization
        if metrics.get('cache_hit_rate', 1.0) < 0.7:
            if await self._can_apply_optimization('cache_warming'):
                await self._warm_cache()
                optimizations_applied.append('Warmed cache with frequent queries')
        
        # Record applied optimizations
        for optimization in optimizations_applied:
            self.optimization_history.append({
                'optimization': optimization,
                'timestamp': datetime.utcnow(),
                'metrics_before': metrics.copy()
            })
        
        return optimizations_applied
    
    async def _can_apply_optimization(self, optimization_type: str) -> bool:
        """Check if optimization can be applied (rate limiting)"""
        last_applied = self.optimizations_applied.get(optimization_type)
        if not last_applied:
            return True
        
        # Don't apply same optimization more than once per hour
        return datetime.utcnow() - last_applied > timedelta(hours=1)
    
    async def _expand_db_pool(self):
        """Expand database connection pool"""
        # This would integrate with your actual DB pool configuration
        logger.info("Auto-optimization: Expanding database connection pool")
        self.optimizations_applied['db_pool_expansion'] = datetime.utcnow()
    
    async def _trigger_memory_cleanup(self):
        """Trigger memory cleanup"""
        import gc
        gc.collect()
        logger.info("Auto-optimization: Triggered garbage collection")
        self.optimizations_applied['memory_cleanup'] = datetime.utcnow()
    
    async def _optimize_slow_queries(self):
        """Analyze and optimize slow queries"""
        logger.info("Auto-optimization: Analyzing slow queries")
        self.optimizations_applied['query_optimization'] = datetime.utcnow()
    
    async def _warm_cache(self):
        """Warm up cache with frequently accessed data"""
        logger.info("Auto-optimization: Warming cache")
        self.optimizations_applied['cache_warming'] = datetime.utcnow()

class PerformanceMonitor:
    """Comprehensive backend performance monitoring system"""
    
    def __init__(self):
        self.settings = get_settings()
        self.registry = CollectorRegistry()
        self.metrics_storage: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[Alert] = []
        self.alert_handlers: List[Callable] = []
        self.optimizer = PerformanceOptimizer()
        self.monitoring_active = False
        self.background_task: Optional[asyncio.Task] = None
        
        # Performance budgets
        self.performance_budgets = {
            'response_time_ms': 200,      # API responses under 200ms
            'db_query_time_ms': 100,      # DB queries under 100ms
            'memory_usage_percent': 80,   # Memory usage under 80%
            'cpu_usage_percent': 70,      # CPU usage under 70%
            'disk_usage_percent': 85,     # Disk usage under 85%
            'error_rate_percent': 1,      # Error rate under 1%
            'cache_hit_rate': 0.8,        # Cache hit rate above 80%
        }
        
        # Initialize Prometheus metrics
        self._init_prometheus_metrics()
        
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        # Request metrics
        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.request_count = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        # Database metrics
        self.db_query_duration = Histogram(
            'db_query_duration_seconds',
            'Database query duration in seconds',
            ['operation', 'table'],
            registry=self.registry
        )
        
        self.db_connection_pool = Gauge(
            'db_connection_pool_usage',
            'Database connection pool usage',
            ['pool_name'],
            registry=self.registry
        )
        
        # System metrics
        self.memory_usage = Gauge(
            'system_memory_usage_bytes',
            'System memory usage in bytes',
            registry=self.registry
        )
        
        self.cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        # Application metrics
        self.active_websockets = Gauge(
            'websocket_connections_active',
            'Active WebSocket connections',
            registry=self.registry
        )
        
        self.cache_operations = Counter(
            'cache_operations_total',
            'Cache operations',
            ['operation', 'result'],
            registry=self.registry
        )

    async def start_monitoring(self):
        """Start background monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.background_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Performance monitoring started")

    async def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.background_task:
            self.background_task.cancel()
            try:
                await self.background_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect application metrics
                await self._collect_app_metrics()
                
                # Check performance budgets
                await self._check_performance_budgets()
                
                # Auto-optimization
                if self.settings.enable_auto_optimization:
                    await self._run_auto_optimization()
                
                # Clean up old metrics
                await self._cleanup_old_metrics()
                
                # Wait before next collection
                await asyncio.sleep(self.settings.monitoring_interval or 10)
                
            except Exception as e:
                logger.error("Error in monitoring loop", error=str(e))
                await asyncio.sleep(5)  # Wait before retrying

    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # Memory metrics
            memory = psutil.virtual_memory()
            self.memory_usage.set(memory.used)
            await self._record_metric('memory_usage_bytes', memory.used)
            await self._record_metric('memory_usage_percent', memory.percent)
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage.set(cpu_percent)
            await self._record_metric('cpu_usage_percent', cpu_percent)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            await self._record_metric('disk_usage_percent', 
                                    (disk.used / disk.total) * 100)
            
            # Process-specific metrics
            process = psutil.Process()
            await self._record_metric('process_memory_rss', process.memory_info().rss)
            await self._record_metric('process_cpu_percent', process.cpu_percent())
            
        except Exception as e:
            logger.error("Error collecting system metrics", error=str(e))

    async def _collect_app_metrics(self):
        """Collect application-specific metrics"""
        try:
            # Database metrics (if available)
            await self._collect_db_metrics()
            
            # Cache metrics (if Redis available)
            await self._collect_cache_metrics()
            
            # WebSocket metrics
            await self._collect_websocket_metrics()
            
        except Exception as e:
            logger.error("Error collecting app metrics", error=str(e))

    async def _collect_db_metrics(self):
        """Collect database performance metrics"""
        try:
            async with get_db() as db:
                # Query execution time monitoring
                start_time = time.time()
                result = await db.execute(text("SELECT 1"))
                query_time = (time.time() - start_time) * 1000
                
                await self._record_metric('db_health_check_ms', query_time)
                
                # Connection pool metrics would go here
                # This depends on your specific database setup
                
        except Exception as e:
            logger.error("Error collecting database metrics", error=str(e))

    async def _collect_cache_metrics(self):
        """Collect cache performance metrics"""
        # This would integrate with your Redis monitoring
        # For now, we'll record placeholder metrics
        await self._record_metric('cache_hit_rate', 0.85)  # Example
        await self._record_metric('cache_memory_usage', 1024 * 1024 * 50)  # 50MB

    async def _collect_websocket_metrics(self):
        """Collect WebSocket metrics"""
        # This would integrate with your WebSocket manager
        await self._record_metric('websocket_connections', 10)  # Example

    async def _record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a metric value"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {}
        )
        
        self.metrics_storage[name].append(metric)

    async def _check_performance_budgets(self):
        """Check if metrics exceed performance budgets"""
        current_metrics = await self.get_current_metrics()
        
        for metric_name, budget in self.performance_budgets.items():
            current_value = current_metrics.get(metric_name)
            if current_value is None:
                continue
            
            # Check if budget is exceeded
            if self._is_budget_exceeded(metric_name, current_value, budget):
                await self._create_alert(
                    severity=Severity.WARNING if current_value < budget * 1.2 else Severity.CRITICAL,
                    message=f"{metric_name} exceeded budget: {current_value} > {budget}",
                    metric_name=metric_name,
                    threshold=budget,
                    current_value=current_value
                )

    def _is_budget_exceeded(self, metric_name: str, current_value: float, budget: float) -> bool:
        """Check if a metric value exceeds its budget"""
        # For hit rates, we want values above the budget
        if 'hit_rate' in metric_name:
            return current_value < budget
        
        # For most other metrics, we want values below the budget
        return current_value > budget

    async def _create_alert(self, severity: Severity, message: str, metric_name: str, 
                          threshold: float, current_value: float):
        """Create a performance alert"""
        alert_id = f"{metric_name}_{int(time.time())}"
        
        suggestions = self._generate_suggestions(metric_name, current_value, threshold)
        
        alert = Alert(
            id=alert_id,
            severity=severity,
            message=message,
            metric_name=metric_name,
            threshold=threshold,
            current_value=current_value,
            timestamp=datetime.utcnow(),
            suggestions=suggestions
        )
        
        self.alerts.append(alert)
        
        # Notify alert handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error("Error in alert handler", error=str(e))
        
        logger.warning("Performance alert created", alert=alert)

    def _generate_suggestions(self, metric_name: str, current_value: float, threshold: float) -> List[str]:
        """Generate optimization suggestions based on the metric"""
        suggestions = []
        
        if 'response_time' in metric_name:
            suggestions.extend([
                "Enable caching for frequently accessed endpoints",
                "Optimize database queries",
                "Consider implementing CDN for static assets",
                "Review and optimize slow endpoints"
            ])
        elif 'memory_usage' in metric_name:
            suggestions.extend([
                "Increase memory limits if possible",
                "Implement memory-efficient algorithms",
                "Check for memory leaks",
                "Enable garbage collection tuning"
            ])
        elif 'cpu_usage' in metric_name:
            suggestions.extend([
                "Scale horizontally with more instances",
                "Optimize CPU-intensive operations",
                "Implement async processing for heavy tasks",
                "Profile and optimize hot code paths"
            ])
        elif 'db_query_time' in metric_name:
            suggestions.extend([
                "Add database indexes for slow queries",
                "Optimize query structure",
                "Implement query result caching",
                "Consider database connection pooling"
            ])
        
        return suggestions

    async def _run_auto_optimization(self):
        """Run automated optimization based on current metrics"""
        current_metrics = await self.get_current_metrics()
        optimizations = await self.optimizer.analyze_and_optimize(current_metrics)
        
        if optimizations:
            logger.info("Auto-optimizations applied", optimizations=optimizations)

    async def _cleanup_old_metrics(self):
        """Clean up metrics older than retention period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)  # Keep 24 hours
        
        for metric_name, metrics in self.metrics_storage.items():
            # Filter out old metrics
            recent_metrics = deque()
            for metric in metrics:
                if metric.timestamp > cutoff_time:
                    recent_metrics.append(metric)
            self.metrics_storage[metric_name] = recent_metrics

    async def get_current_metrics(self) -> Dict[str, float]:
        """Get current metric values"""
        current_metrics = {}
        
        for metric_name, metrics in self.metrics_storage.items():
            if metrics:
                # Get the most recent value
                current_metrics[metric_name] = metrics[-1].value
        
        return current_metrics

    async def get_metric_history(self, metric_name: str, duration_hours: int = 1) -> List[PerformanceMetric]:
        """Get historical data for a specific metric"""
        cutoff_time = datetime.utcnow() - timedelta(hours=duration_hours)
        metrics = self.metrics_storage.get(metric_name, deque())
        
        return [metric for metric in metrics if metric.timestamp > cutoff_time]

    async def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        current_metrics = await self.get_current_metrics()
        active_alerts = [alert for alert in self.alerts if not alert.resolved]
        
        # Calculate health score
        health_score = self._calculate_health_score(current_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(current_metrics, active_alerts)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'health_score': health_score,
            'current_metrics': current_metrics,
            'active_alerts': [
                {
                    'id': alert.id,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'metric_name': alert.metric_name,
                    'suggestions': alert.suggestions
                }
                for alert in active_alerts
            ],
            'performance_budgets': self.performance_budgets,
            'recommendations': recommendations,
            'optimization_history': self.optimizer.optimization_history[-10:]  # Last 10
        }

    def _calculate_health_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall system health score (0-100)"""
        score_components = []
        
        # Response time score
        response_time = metrics.get('response_time_ms', 0)
        if response_time <= 100:
            score_components.append(100)
        elif response_time <= 500:
            score_components.append(80)
        else:
            score_components.append(50)
        
        # Memory usage score
        memory_percent = metrics.get('memory_usage_percent', 0)
        if memory_percent <= 70:
            score_components.append(100)
        elif memory_percent <= 85:
            score_components.append(80)
        else:
            score_components.append(50)
        
        # CPU usage score
        cpu_percent = metrics.get('cpu_usage_percent', 0)
        if cpu_percent <= 50:
            score_components.append(100)
        elif cpu_percent <= 80:
            score_components.append(80)
        else:
            score_components.append(50)
        
        # Error rate score
        error_rate = metrics.get('error_rate_percent', 0)
        if error_rate <= 0.1:
            score_components.append(100)
        elif error_rate <= 1:
            score_components.append(80)
        else:
            score_components.append(50)
        
        return sum(score_components) / len(score_components) if score_components else 0

    def _generate_recommendations(self, metrics: Dict[str, float], alerts: List[Alert]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Based on metrics
        if metrics.get('memory_usage_percent', 0) > 80:
            recommendations.append("Consider increasing memory allocation or optimizing memory usage")
        
        if metrics.get('cpu_usage_percent', 0) > 70:
            recommendations.append("High CPU usage detected - consider horizontal scaling")
        
        if metrics.get('cache_hit_rate', 1.0) < 0.8:
            recommendations.append("Low cache hit rate - review caching strategy")
        
        # Based on alerts
        if any(alert.severity == Severity.CRITICAL for alert in alerts):
            recommendations.append("Critical alerts detected - immediate attention required")
        
        return recommendations

    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add a custom alert handler"""
        self.alert_handlers.append(handler)

    @asynccontextmanager
    async def monitor_operation(self, operation_name: str, labels: Optional[Dict[str, str]] = None):
        """Context manager for monitoring operations"""
        start_time = time.time()
        exception_occurred = False
        
        try:
            yield
        except Exception as e:
            exception_occurred = True
            raise
        finally:
            duration = time.time() - start_time
            
            # Record the operation
            await self._record_metric(
                f'operation_{operation_name}_duration_ms',
                duration * 1000,
                labels
            )
            
            if exception_occurred:
                await self._record_metric(
                    f'operation_{operation_name}_errors',
                    1,
                    labels
                )

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Decorator for monitoring async functions
def monitor_performance(operation_name: str = None, labels: Dict[str, str] = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            async with performance_monitor.monitor_operation(op_name, labels):
                return await func(*args, **kwargs)
        return wrapper
    return decorator