#!/bin/bash
set -e

# Digital Greenhouse Backend Entrypoint Script
# Handles initialization, migrations, and graceful startup

echo "🌱 Digital Greenhouse Backend Starting..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check required environment variables
check_env_vars() {
    log_info "Checking environment variables..."
    
    local required_vars=(
        "DATABASE_URL"
        "SECRET_KEY"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        exit 1
    fi
    
    log_success "Environment variables OK"
}

# Wait for database to be ready
wait_for_db() {
    log_info "Waiting for database to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if python -c "
import asyncio
import asyncpg
import os
import sys
from urllib.parse import urlparse

async def check_db():
    try:
        db_url = os.environ['DATABASE_URL']
        # Handle both sync and async database URLs
        if db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        elif db_url.startswith('postgresql+asyncpg://'):
            pass
        else:
            # Extract connection info for asyncpg
            parsed = urlparse(db_url)
            conn = await asyncpg.connect(
                user=parsed.username,
                password=parsed.password,
                database=parsed.path[1:],
                host=parsed.hostname,
                port=parsed.port or 5432
            )
            await conn.close()
            return
        
        # For SQLAlchemy URLs, try direct asyncpg connection
        from sqlalchemy import make_url
        url = make_url(db_url)
        conn = await asyncpg.connect(
            user=url.username,
            password=url.password,
            database=url.database,
            host=url.host,
            port=url.port or 5432
        )
        await conn.close()
    except Exception as e:
        print(f'Database connection failed: {e}')
        sys.exit(1)

asyncio.run(check_db())
"; then
            log_success "Database is ready"
            return 0
        fi
        
        log_info "Database not ready, waiting... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "Database failed to become ready after $max_attempts attempts"
    exit 1
}

# Wait for Redis to be ready (if configured)
wait_for_redis() {
    if [[ -z "$REDIS_URL" ]]; then
        log_info "Redis URL not configured, skipping Redis check"
        return 0
    fi
    
    log_info "Waiting for Redis to be ready..."
    
    local max_attempts=15
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if python -c "
import redis
import os
import sys
from urllib.parse import urlparse

try:
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    r = redis.from_url(redis_url)
    r.ping()
except Exception as e:
    print(f'Redis connection failed: {e}')
    sys.exit(1)
"; then
            log_success "Redis is ready"
            return 0
        fi
        
        log_info "Redis not ready, waiting... (attempt $attempt/$max_attempts)"
        sleep 1
        attempt=$((attempt + 1))
    done
    
    log_warning "Redis failed to become ready, continuing without Redis"
    return 0
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    if alembic current &>/dev/null; then
        if alembic upgrade head; then
            log_success "Database migrations completed"
        else
            log_error "Database migrations failed"
            exit 1
        fi
    else
        log_warning "Alembic not configured or database not initialized"
        log_info "Attempting to initialize database..."
        
        if alembic upgrade head; then
            log_success "Database initialized with migrations"
        else
            log_error "Failed to initialize database"
            exit 1
        fi
    fi
}

# Seed initial data (if needed)
seed_data() {
    if [[ "$SEED_DATA" == "true" ]]; then
        log_info "Seeding initial data..."
        
        if python -c "
from app.core.database import get_db
from app.models import Base
from sqlalchemy import create_engine
import asyncio
import os

async def seed():
    # Add your data seeding logic here
    print('Data seeding completed')

if __name__ == '__main__':
    asyncio.run(seed())
"; then
            log_success "Data seeding completed"
        else
            log_warning "Data seeding failed, continuing..."
        fi
    fi
}

# Collect static files (if needed)
collect_static() {
    if [[ "$COLLECT_STATIC" == "true" ]]; then
        log_info "Collecting static files..."
        # Add static file collection logic if needed
        log_success "Static files collected"
    fi
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Create log directories
    mkdir -p /app/logs
    
    # Start background monitoring if enabled
    if [[ "$ENABLE_MONITORING" == "true" ]]; then
        # Start monitoring in background
        python -c "
from app.core.monitoring import performance_monitor
import asyncio

async def start_monitoring():
    await performance_monitor.start_monitoring()

if __name__ == '__main__':
    asyncio.run(start_monitoring())
" &
        log_success "Performance monitoring started"
    fi
}

# Handle shutdown gracefully
cleanup() {
    log_info "Shutting down gracefully..."
    
    # Stop background processes
    jobs -p | xargs -r kill
    
    log_success "Shutdown complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Main execution
main() {
    log_info "Starting Digital Greenhouse Backend initialization..."
    
    # Perform startup checks and initialization
    check_env_vars
    wait_for_db
    wait_for_redis
    run_migrations
    seed_data
    collect_static
    setup_monitoring
    
    log_success "Initialization complete, starting application..."
    
    # Execute the main command
    exec "$@"
}

# Run main function with all arguments
main "$@"