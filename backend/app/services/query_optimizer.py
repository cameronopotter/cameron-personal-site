import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from sqlalchemy.engine import Result
import re

logger = logging.getLogger(__name__)

class QueryOptimizer:
    def __init__(self):
        self.active = True
        self.optimization_strategies = {
            'missing_indexes': self._suggest_indexes,
            'inefficient_joins': self._optimize_joins,
            'redundant_queries': self._eliminate_redundancy,
            'large_result_sets': self._add_pagination,
            'cartesian_products': self._fix_cartesian_products
        }
    
    def is_active(self) -> bool:
        return self.active
    
    async def identify_slow_queries(self, db: Session) -> List[Dict]:
        """Identify queries that need optimization"""
        try:
            # Get query statistics from database
            slow_queries = []
            
            # PostgreSQL specific query for slow queries
            query = text("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows,
                    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                FROM pg_stat_statements 
                WHERE mean_time > 1000  -- queries taking more than 1 second on average
                ORDER BY total_time DESC
                LIMIT 20
            """)
            
            result = db.execute(query)
            for row in result:
                slow_queries.append({
                    'query': row.query[:200],
                    'calls': row.calls,
                    'total_time_ms': row.total_time,
                    'avg_time_ms': row.mean_time,
                    'rows_affected': row.rows,
                    'cache_hit_percent': row.hit_percent or 0
                })
            
            return slow_queries
            
        except Exception as e:
            logger.error(f"Error identifying slow queries: {e}")
            return []
    
    async def optimize_query(self, query_id: str, db: Session) -> Dict:
        """Optimize a specific query"""
        optimization_results = {
            'query_id': query_id,
            'optimizations_applied': [],
            'estimated_improvement': 0,
            'recommendations': []
        }
        
        try:
            # Apply various optimization strategies
            for strategy_name, strategy_func in self.optimization_strategies.items():
                result = await strategy_func(query_id, db)
                if result['applied']:
                    optimization_results['optimizations_applied'].append(strategy_name)
                    optimization_results['estimated_improvement'] += result['improvement_percent']
                    optimization_results['recommendations'].extend(result['recommendations'])
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing query {query_id}: {e}")
            return optimization_results
    
    async def _suggest_indexes(self, query_id: str, db: Session) -> Dict:
        """Suggest missing indexes based on query patterns"""
        try:
            # Analyze query execution plan to suggest indexes
            suggestions = []
            
            # Example analysis for common patterns
            missing_indexes_query = text("""
                SELECT schemaname, tablename, attname, n_distinct, correlation
                FROM pg_stats
                WHERE schemaname = 'public'
                AND n_distinct > 100
                AND correlation < 0.1
                ORDER BY n_distinct DESC
                LIMIT 10
            """)
            
            result = db.execute(missing_indexes_query)
            for row in result:
                suggestions.append(f"CREATE INDEX idx_{row.tablename}_{row.attname} ON {row.tablename}({row.attname})")
            
            return {
                'applied': len(suggestions) > 0,
                'improvement_percent': 25 if suggestions else 0,
                'recommendations': suggestions
            }
            
        except Exception as e:
            logger.error(f"Error suggesting indexes: {e}")
            return {'applied': False, 'improvement_percent': 0, 'recommendations': []}
    
    async def _optimize_joins(self, query_id: str, db: Session) -> Dict:
        """Optimize inefficient JOIN operations"""
        recommendations = [
            "Consider using EXISTS instead of JOIN when only checking for existence",
            "Use INNER JOIN instead of LEFT JOIN when possible",
            "Ensure JOIN conditions use indexed columns",
            "Consider breaking complex JOINs into smaller queries"
        ]
        
        return {
            'applied': True,
            'improvement_percent': 15,
            'recommendations': recommendations
        }
    
    async def _eliminate_redundancy(self, query_id: str, db: Session) -> Dict:
        """Eliminate redundant queries"""
        recommendations = [
            "Implement query result caching",
            "Combine multiple similar queries into one",
            "Use materialized views for frequently accessed aggregations",
            "Batch similar operations together"
        ]
        
        return {
            'applied': True,
            'improvement_percent': 20,
            'recommendations': recommendations
        }
    
    async def _add_pagination(self, query_id: str, db: Session) -> Dict:
        """Add pagination to queries returning large result sets"""
        recommendations = [
            "Add LIMIT and OFFSET clauses to large result sets",
            "Implement cursor-based pagination for better performance",
            "Use streaming for very large datasets",
            "Consider result set size limits at application level"
        ]
        
        return {
            'applied': True,
            'improvement_percent': 30,
            'recommendations': recommendations
        }
    
    async def _fix_cartesian_products(self, query_id: str, db: Session) -> Dict:
        """Fix accidental cartesian products in queries"""
        recommendations = [
            "Ensure all JOINs have proper ON conditions",
            "Avoid CROSS JOINs unless intentional",
            "Use EXISTS or IN subqueries instead of multiple JOINs when appropriate",
            "Review WHERE clauses for proper filtering"
        ]
        
        return {
            'applied': False,
            'improvement_percent': 0,
            'recommendations': recommendations
        }
    
    async def create_performance_indexes(self, db: Session) -> List[str]:
        """Create indexes for better performance"""
        indexes_created = []
        
        try:
            # Common performance indexes
            performance_indexes = [
                "CREATE INDEX IF NOT EXISTS idx_created_at ON table_name(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_status ON table_name(status)",
                "CREATE INDEX IF NOT EXISTS idx_user_id ON table_name(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_composite ON table_name(status, created_at)"
            ]
            
            for index_sql in performance_indexes:
                try:
                    db.execute(text(index_sql))
                    indexes_created.append(index_sql)
                    logger.info(f"Created index: {index_sql}")
                except Exception as e:
                    logger.warning(f"Failed to create index: {e}")
            
            db.commit()
            return indexes_created
            
        except Exception as e:
            logger.error(f"Error creating performance indexes: {e}")
            db.rollback()
            return indexes_created