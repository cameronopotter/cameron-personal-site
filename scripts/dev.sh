#!/bin/bash

# Digital Greenhouse Development Server
# Easy development environment startup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}🌱 Starting Digital Greenhouse Development Environment 🌱${NC}\n"

# Check if .env exists
if [[ ! -f ".env" ]]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo -e "${YELLOW}Please run the setup script first: ./scripts/setup.sh${NC}"
    exit 1
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check ports
echo -e "${BLUE}🔍 Checking ports...${NC}"

if check_port 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 is already in use (Frontend)${NC}"
    FRONTEND_PORT_CONFLICT=true
else
    echo -e "${GREEN}✅ Port 3000 available (Frontend)${NC}"
    FRONTEND_PORT_CONFLICT=false
fi

if check_port 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use (Backend)${NC}"
    BACKEND_PORT_CONFLICT=true
else
    echo -e "${GREEN}✅ Port 8000 available (Backend)${NC}"
    BACKEND_PORT_CONFLICT=false
fi

if check_port 5432; then
    echo -e "${GREEN}✅ PostgreSQL detected on port 5432${NC}"
    POSTGRES_RUNNING=true
else
    echo -e "${YELLOW}⚠️  PostgreSQL not detected on port 5432${NC}"
    POSTGRES_RUNNING=false
fi

if check_port 6379; then
    echo -e "${GREEN}✅ Redis detected on port 6379${NC}"
    REDIS_RUNNING=true
else
    echo -e "${YELLOW}⚠️  Redis not detected on port 6379${NC}"
    REDIS_RUNNING=false
fi

echo ""

# Start database services if not running
if [[ "$POSTGRES_RUNNING" == false || "$REDIS_RUNNING" == false ]]; then
    echo -e "${BLUE}🐳 Starting database services...${NC}"
    
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose up -d postgres redis
        echo -e "${GREEN}✅ Database services started${NC}"
        
        # Wait a moment for services to initialize
        echo -e "${BLUE}⏳ Waiting for services to initialize...${NC}"
        sleep 5
    else
        echo -e "${RED}❌ Docker Compose not found. Please install Docker or start PostgreSQL and Redis manually.${NC}"
        echo -e "${YELLOW}   PostgreSQL: database 'digital_greenhouse', user 'garden_user'${NC}"
        echo -e "${YELLOW}   Redis: default configuration on port 6379${NC}"
        exit 1
    fi
fi

# Function to start backend
start_backend() {
    echo -e "${PURPLE}⚡ Starting FastAPI Backend...${NC}"
    cd backend
    
    # Activate virtual environment if it exists
    if [[ -d "venv" ]]; then
        source venv/bin/activate
    fi
    
    # Check if uvicorn is available
    if ! command -v uvicorn >/dev/null 2>&1; then
        echo -e "${RED}❌ uvicorn not found. Installing backend dependencies...${NC}"
        pip install -r requirements.txt
    fi
    
    echo -e "${GREEN}🚀 Backend starting on http://localhost:8000${NC}"
    echo -e "${BLUE}   API Documentation: http://localhost:8000/docs${NC}"
    
    # Start with auto-reload for development
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ..
    return 0
}

# Function to start frontend
start_frontend() {
    echo -e "${PURPLE}🎨 Starting React Frontend...${NC}"
    cd frontend
    
    # Check if node_modules exists
    if [[ ! -d "node_modules" ]]; then
        echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
        npm install
    fi
    
    echo -e "${GREEN}🚀 Frontend starting on http://localhost:3000${NC}"
    echo -e "${BLUE}   Development server with hot reload enabled${NC}"
    
    # Start development server
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
    return 0
}

# Function to start background tasks
start_celery() {
    echo -e "${PURPLE}🔄 Starting Background Tasks...${NC}"
    cd backend
    
    # Activate virtual environment if it exists
    if [[ -d "venv" ]]; then
        source venv/bin/activate
    fi
    
    # Start Celery worker in background
    celery -A app.core.celery_app worker --loglevel=info --detach
    
    # Start Celery beat scheduler
    celery -A app.core.celery_app beat --loglevel=info --detach
    
    echo -e "${GREEN}✅ Background tasks started${NC}"
    
    cd ..
}

# Trap to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down development environment...${NC}"
    
    # Kill frontend and backend processes
    if [[ -n "$FRONTEND_PID" ]]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    if [[ -n "$BACKEND_PID" ]]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    # Stop Celery processes
    pkill -f "celery.*app.core.celery_app" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

trap cleanup INT TERM

# Parse command line arguments
case "${1:-both}" in
    "frontend"|"f")
        echo -e "${CYAN}🎨 Starting Frontend Only${NC}\n"
        start_frontend
        wait $FRONTEND_PID
        ;;
    "backend"|"b")
        echo -e "${CYAN}⚡ Starting Backend Only${NC}\n"
        start_backend
        wait $BACKEND_PID
        ;;
    "tasks"|"t")
        echo -e "${CYAN}🔄 Starting Background Tasks Only${NC}\n"
        start_celery
        echo -e "${GREEN}Background tasks are running. Press Ctrl+C to stop.${NC}"
        while true; do sleep 1; done
        ;;
    "both"|*)
        echo -e "${CYAN}🚀 Starting Full Development Environment${NC}\n"
        
        # Start backend first
        start_backend
        sleep 2
        
        # Start frontend
        start_frontend
        sleep 2
        
        # Start background tasks
        start_celery
        
        echo ""
        echo -e "${GREEN}🌱 Digital Greenhouse is now running! 🌱${NC}"
        echo ""
        echo -e "${CYAN}📍 URLs:${NC}"
        echo -e "   ${GREEN}🎨 Frontend:${NC} http://localhost:3000"
        echo -e "   ${GREEN}⚡ Backend API:${NC} http://localhost:8000"
        echo -e "   ${GREEN}📖 API Docs:${NC} http://localhost:8000/docs"
        echo -e "   ${GREEN}🔄 WebSocket:${NC} ws://localhost:8000/ws"
        echo ""
        echo -e "${CYAN}💡 Tips:${NC}"
        echo -e "   • Edit files and see live updates"
        echo -e "   • Check the browser console for debug info"
        echo -e "   • API documentation is interactive at /docs"
        echo -e "   • Press ${YELLOW}Ctrl+C${NC} to stop all services"
        echo ""
        echo -e "${PURPLE}🌟 Happy coding in your Digital Greenhouse! 🌟${NC}"
        
        # Wait for processes
        wait
        ;;
esac