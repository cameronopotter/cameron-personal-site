import asyncio
import logging
import time
from typing import Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import get_db, get_query_stats

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self):
        self.running = False
        self.monitoring_task = None
        self.metrics_history = []
        self.alert_thresholds = {
            'slow_query_threshold': 1.0,  # seconds
            'connection_threshold': 80,   # percentage
            'memory_threshold': 85,       # percentage
            'cpu_threshold': 90          # percentage
        }
    
    def is_running(self) -> bool:
        return self.running
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        if self.running:
            return
        
        self.running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        if not self.running:
            return
        
        self.running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect metrics every 30 seconds
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only last 100 entries (50 minutes of data)
                if len(self.metrics_history) > 100:
                    self.metrics_history.pop(0)
                
                # Check for alerts
                await self._check_alerts(metrics)
                
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _collect_metrics(self) -> Dict:
        """Collect current performance metrics"""
        db = next(get_db())
        try:
            metrics = {
                'timestamp': time.time(),
                'database': await self._get_database_metrics(db),
                'queries': await self._get_query_metrics(),
                'connections': await self._get_connection_metrics(db),
                'system': await self._get_system_metrics()
            }
            return metrics
        finally:
            db.close()
    
    async def _get_database_metrics(self, db: Session) -> Dict:
        """Get database performance metrics"""
        try:
            # Get database size and activity
            db_metrics_query = text("""
                SELECT 
                    pg_database_size(current_database()) as db_size,
                    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                    (SELECT count(*) FROM pg_stat_activity) as total_connections
            """)
            
            result = db.execute(db_metrics_query).fetchone()
            
            # Get cache hit ratio
            cache_query = text("""
                SELECT 
                    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_hit_ratio
                FROM pg_statio_user_tables
            """)
            
            cache_result = db.execute(cache_query).fetchone()
            
            return {
                'database_size_bytes': result.db_size if result else 0,
                'active_connections': result.active_connections if result else 0,
                'total_connections': result.total_connections if result else 0,
                'cache_hit_ratio': float(cache_result.cache_hit_ratio or 0) if cache_result else 0
            }
            
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
            return {}
    
    async def _get_query_metrics(self) -> Dict:
        """Get query performance metrics"""
        try:
            query_stats = get_query_stats()
            
            if not query_stats:
                return {'total_queries': 0, 'slow_queries': 0, 'avg_query_time': 0}
            
            total_queries = sum(stats['count'] for stats in query_stats.values())
            slow_queries = sum(1 for stats in query_stats.values() 
                             if stats['avg_time'] > self.alert_thresholds['slow_query_threshold'])
            avg_query_time = sum(stats['avg_time'] * stats['count'] for stats in query_stats.values()) / total_queries if total_queries > 0 else 0
            
            return {
                'total_queries': total_queries,
                'slow_queries': slow_queries,
                'avg_query_time': avg_query_time,
                'unique_queries': len(query_stats)
            }
            
        except Exception as e:
            logger.error(f"Error collecting query metrics: {e}")
            return {}
    
    async def _get_connection_metrics(self, db: Session) -> Dict:
        """Get database connection metrics"""
        try:
            conn_query = text("""
                SELECT 
                    max_conn,
                    used,
                    res_for_super,
                    max_conn-used-res_for_super as available
                FROM 
                    (SELECT count(*) used FROM pg_stat_activity) s,
                    (SELECT setting::int max_conn FROM pg_settings WHERE name='max_connections') m,
                    (SELECT setting::int res_for_super FROM pg_settings WHERE name='superuser_reserved_connections') r
            """)
            
            result = db.execute(conn_query).fetchone()
            
            if result:
                usage_percent = (result.used / result.max_conn) * 100
                return {
                    'max_connections': result.max_conn,
                    'used_connections': result.used,
                    'available_connections': result.available,
                    'usage_percent': usage_percent
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error collecting connection metrics: {e}")
            return {}
    
    async def _get_system_metrics(self) -> Dict:
        """Get system performance metrics (simplified)"""
        # In a real implementation, you would use system monitoring tools
        # For now, return placeholder values
        return {
            'cpu_percent': 25.0,
            'memory_percent': 45.0,
            'disk_io_read': 1000,
            'disk_io_write': 500
        }
    
    async def _check_alerts(self, metrics: Dict):
        """Check metrics against alert thresholds"""
        alerts = []
        
        # Check slow queries
        query_metrics = metrics.get('queries', {})
        if query_metrics.get('slow_queries', 0) > 5:
            alerts.append(f"High number of slow queries: {query_metrics['slow_queries']}")
        
        # Check connection usage
        conn_metrics = metrics.get('connections', {})
        if conn_metrics.get('usage_percent', 0) > self.alert_thresholds['connection_threshold']:
            alerts.append(f"High connection usage: {conn_metrics['usage_percent']:.1f}%")
        
        # Check system metrics
        system_metrics = metrics.get('system', {})
        if system_metrics.get('memory_percent', 0) > self.alert_thresholds['memory_threshold']:
            alerts.append(f"High memory usage: {system_metrics['memory_percent']:.1f}%")
        
        if system_metrics.get('cpu_percent', 0) > self.alert_thresholds['cpu_threshold']:
            alerts.append(f"High CPU usage: {system_metrics['cpu_percent']:.1f}%")
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"PERFORMANCE ALERT: {alert}")
    
    async def get_current_metrics(self) -> Dict:
        """Get current performance metrics"""
        if not self.metrics_history:
            return {"message": "No metrics collected yet"}
        
        latest_metrics = self.metrics_history[-1]
        
        # Add summary statistics
        if len(self.metrics_history) >= 2:
            prev_metrics = self.metrics_history[-2]
            
            # Calculate trends
            db_current = latest_metrics.get('database', {})
            db_prev = prev_metrics.get('database', {})
            
            trends = {}
            if db_current and db_prev:
                trends['connection_change'] = db_current.get('active_connections', 0) - db_prev.get('active_connections', 0)
                trends['cache_hit_change'] = db_current.get('cache_hit_ratio', 0) - db_prev.get('cache_hit_ratio', 0)
            
            latest_metrics['trends'] = trends
        
        return latest_metrics
    
    async def get_metrics_history(self, limit: int = 50) -> List[Dict]:
        """Get historical metrics data"""
        return self.metrics_history[-limit:] if self.metrics_history else []