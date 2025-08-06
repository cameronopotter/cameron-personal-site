#!/bin/bash

# Health check scripts for Digital Greenhouse services

# Determine which service to check based on script name or environment
SERVICE_TYPE="${1:-${SERVICE_TYPE:-auto}}"

# Auto-detect service type if not specified
if [[ "$SERVICE_TYPE" == "auto" ]]; then
    if [[ "$0" == *"healthcheck-backend"* ]] || [[ -n "$DATABASE_URL" ]]; then
        SERVICE_TYPE="backend"
    else
        SERVICE_TYPE="frontend"
    fi
fi

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging functions
log_success() {
    echo -e "${GREEN}[HEALTH]${NC} $1"
}

log_error() {
    echo -e "${RED}[HEALTH]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[HEALTH]${NC} $1"
}

# Frontend health check
check_frontend_health() {
    local port=${PORT:-8080}
    local host=${HOST:-localhost}
    
    # Check if nginx is running
    if ! pgrep nginx > /dev/null; then
        log_error "Nginx process not found"
        return 1
    fi
    
    # Check if port is listening
    if ! netstat -ln 2>/dev/null | grep ":$port " > /dev/null; then
        log_error "Port $port is not listening"
        return 1
    fi
    
    # Check HTTP response
    if command -v curl > /dev/null; then
        local response=$(curl -s -o /dev/null -w "%{http_code}" "http://$host:$port/health" --connect-timeout 5 --max-time 10)
        if [[ "$response" != "200" ]]; then
            log_error "Health endpoint returned status: $response"
            return 1
        fi
    elif command -v wget > /dev/null; then
        if ! wget -q --spider --timeout=10 "http://$host:$port/health"; then
            log_error "Health endpoint check failed (wget)"
            return 1
        fi
    else
        log_warning "No curl or wget available, skipping HTTP check"
    fi
    
    # Check if main files exist
    if [[ ! -f "/usr/share/nginx/html/index.html" ]]; then
        log_error "Main index.html file not found"
        return 1
    fi
    
    log_success "Frontend health check passed"
    return 0
}

# Backend health check
check_backend_health() {
    local port=${PORT:-8000}
    local host=${HOST:-0.0.0.0}
    
    # Check if Python process is running
    if ! pgrep -f "python.*app" > /dev/null && ! pgrep -f "gunicorn.*app" > /dev/null; then
        log_error "Application process not found"
        return 1
    fi
    
    # Check if port is listening
    if ! netstat -ln 2>/dev/null | grep ":$port " > /dev/null; then
        log_error "Port $port is not listening"
        return 1
    fi
    
    # Check health endpoint
    if command -v curl > /dev/null; then
        local response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/health" --connect-timeout 5 --max-time 10)
        if [[ "$response" != "200" ]]; then
            log_error "Health endpoint returned status: $response"
            return 1
        fi
    elif command -v wget > /dev/null; then
        if ! wget -q --spider --timeout=10 "http://localhost:$port/health"; then
            log_error "Health endpoint check failed (wget)"
            return 1
        fi
    else
        # Fallback: check with Python
        python3 -c "
import urllib.request
import urllib.error
import socket

try:
    with urllib.request.urlopen('http://localhost:$port/health', timeout=10) as response:
        if response.status != 200:
            print('Health check failed: status', response.status)
            exit(1)
except urllib.error.URLError as e:
    print('Health check failed:', str(e))
    exit(1)
except socket.timeout:
    print('Health check timeout')
    exit(1)
except Exception as e:
    print('Health check error:', str(e))
    exit(1)
" || {
            log_error "Health endpoint check failed (python)"
            return 1
        }
    fi
    
    # Check database connectivity (if configured)
    if [[ -n "$DATABASE_URL" ]]; then
        python3 -c "
import asyncio
import sys
import os

async def check_db():
    try:
        from app.core.database import get_db
        # Simple database check
        async for db in get_db():
            # Try a simple query
            result = await db.execute('SELECT 1')
            break
    except ImportError:
        # Fallback for environments where app might not be available
        import asyncpg
        from urllib.parse import urlparse
        
        try:
            db_url = os.environ.get('DATABASE_URL', '')
            if 'postgresql' in db_url:
                parsed = urlparse(db_url.replace('postgresql+asyncpg://', 'postgresql://'))
                conn = await asyncpg.connect(
                    user=parsed.username,
                    password=parsed.password,
                    database=parsed.path[1:] if parsed.path else None,
                    host=parsed.hostname,
                    port=parsed.port or 5432
                )
                await conn.fetchval('SELECT 1')
                await conn.close()
        except Exception as db_error:
            print(f'Database check failed: {db_error}')
            sys.exit(1)
    except Exception as e:
        print(f'Database check failed: {e}')
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(check_db())
" || {
            log_error "Database connectivity check failed"
            return 1
        }
    fi
    
    # Check Redis connectivity (if configured)
    if [[ -n "$REDIS_URL" ]]; then
        python3 -c "
import redis
import os

try:
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    r = redis.from_url(redis_url)
    r.ping()
except Exception as e:
    print(f'Redis check failed: {e}')
    exit(1)
" || {
            log_warning "Redis connectivity check failed (non-critical)"
        }
    fi
    
    log_success "Backend health check passed"
    return 0
}

# Check system resources
check_system_resources() {
    local warn_memory_percent=80
    local warn_disk_percent=85
    
    # Memory check
    if command -v free > /dev/null; then
        local memory_usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100)}')
        if [[ "$memory_usage" -gt "$warn_memory_percent" ]]; then
            log_warning "High memory usage: ${memory_usage}%"
        fi
    fi
    
    # Disk space check
    if command -v df > /dev/null; then
        local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
        if [[ "$disk_usage" -gt "$warn_disk_percent" ]]; then
            log_warning "High disk usage: ${disk_usage}%"
        fi
    fi
}

# Main health check function
main() {
    local exit_code=0
    
    case "$SERVICE_TYPE" in
        "frontend")
            check_frontend_health || exit_code=1
            ;;
        "backend")
            check_backend_health || exit_code=1
            ;;
        *)
            log_error "Unknown service type: $SERVICE_TYPE"
            exit_code=1
            ;;
    esac
    
    # Always check system resources
    check_system_resources
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "Overall health check passed"
    else
        log_error "Health check failed"
    fi
    
    exit $exit_code
}

# Run main function
main "$@"