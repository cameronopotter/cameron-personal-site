"""
Database configuration and connection management for Digital Greenhouse API
"""

import time
import os
import logging
from typing import AsyncGenerator, Generator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from pydantic_settings import BaseSettings

from app.models.base import Base

logger = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    
    # Database URLs
    database_url: str = "postgresql://postgres:password@localhost:5432/digital_greenhouse"
    async_database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/digital_greenhouse"
    test_database_url: str = "postgresql://postgres:password@localhost:5432/digital_greenhouse_test"
    
    # Connection pool settings
    pool_size: int = 20
    max_overflow: int = 30
    pool_pre_ping: bool = True
    pool_recycle: int = 300
    
    # Query settings
    echo_sql: bool = False
    slow_query_threshold: float = 1.0
    
    class Config:
        env_file = ".env"
        env_prefix = "DB_"


# Initialize settings
db_settings = DatabaseSettings()

# Async database engine for main operations
async_engine = create_async_engine(
    db_settings.async_database_url,
    echo=db_settings.echo_sql,
    pool_size=db_settings.pool_size,
    max_overflow=db_settings.max_overflow,
    pool_pre_ping=db_settings.pool_pre_ping,
    pool_recycle=db_settings.pool_recycle,
    future=True
)

# Sync engine for migrations and background tasks
sync_engine = create_engine(
    db_settings.database_url,
    echo=db_settings.echo_sql,
    pool_size=db_settings.pool_size,
    max_overflow=db_settings.max_overflow,
    pool_pre_ping=db_settings.pool_pre_ping,
    pool_recycle=db_settings.pool_recycle,
    connect_args={
        "options": "-c default_transaction_isolation=read_committed"
    }
)

# Session makers
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

SyncSessionLocal = sessionmaker(
    sync_engine,
    autoflush=False,
    autocommit=False
)

# Metadata for migrations
metadata = MetaData()

# Query monitoring
query_stats = {}


@event.listens_for(sync_engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Track query start time for performance monitoring"""
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.debug(f"Start Query: {statement[:100]}...")


@event.listens_for(sync_engine, "after_cursor_execute") 
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Monitor query execution time and log slow queries"""
    total = time.time() - conn.info['query_start_time'].pop(-1)
    
    # Log slow queries
    if total > db_settings.slow_query_threshold:
        logger.warning(f"Slow query ({total:.2f}s): {statement[:200]}...")
        
        # Store in query stats for analysis
        query_hash = hash(statement)
        if query_hash not in query_stats:
            query_stats[query_hash] = {
                'statement': statement[:500],
                'count': 0,
                'total_time': 0,
                'avg_time': 0,
                'max_time': 0
            }
        
        stats = query_stats[query_hash]
        stats['count'] += 1
        stats['total_time'] += total
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['max_time'] = max(stats['max_time'], total)


# Database dependencies
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Async database session dependency for FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Generator[Session, None, None]:
    """Sync database session dependency for background tasks"""
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@asynccontextmanager
async def get_async_db_context() -> AsyncSession:
    """Async context manager for database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Database management functions
async def create_tables():
    """Create all database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def create_sync_tables():
    """Create all database tables synchronously"""
    Base.metadata.create_all(bind=sync_engine)


def drop_sync_tables():
    """Drop all database tables synchronously"""
    Base.metadata.drop_all(bind=sync_engine)


async def check_database_connection() -> bool:
    """Check if database connection is healthy"""
    try:
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


def get_query_stats():
    """Get current query performance statistics"""
    return query_stats


def reset_query_stats():
    """Reset query performance statistics"""
    global query_stats
    query_stats = {}


# Database initialization
async def init_database():
    """Initialize database with tables and basic configuration"""
    logger.info("Initializing database...")
    
    try:
        # Create tables
        await create_tables()
        logger.info("Database tables created successfully")
        
        # Check connection
        if await check_database_connection():
            logger.info("Database connection verified")
        else:
            raise Exception("Database connection verification failed")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


# Database cleanup
async def close_database():
    """Close database connections"""
    logger.info("Closing database connections...")
    await async_engine.dispose()
    sync_engine.dispose()
    logger.info("Database connections closed")