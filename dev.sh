#!/bin/bash

# Digital Greenhouse - Development Server
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Garden banner
echo -e "${GREEN}"
echo "🌱 Starting Digital Greenhouse Development Environment 🌱"
echo -e "${NC}"

# Check if setup was run
if [[ ! -f ".env" ]]; then
    echo -e "${RED}❌ Setup not completed!${NC}"
    echo -e "${YELLOW}Please run: ./setup.sh${NC}"
    exit 1
fi

if [[ ! -d "backend/venv" ]]; then
    echo -e "${RED}❌ Backend not set up!${NC}"
    echo -e "${YELLOW}Please run: ./setup.sh${NC}"
    exit 1
fi

if [[ ! -d "frontend/node_modules" ]]; then
    echo -e "${RED}❌ Frontend not set up!${NC}"
    echo -e "${YELLOW}Please run: ./setup.sh${NC}"
    exit 1
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check ports and kill conflicting processes
echo -e "${BLUE}🔍 Checking ports...${NC}"

if check_port 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 in use, clearing...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

if check_port 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 in use, clearing...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Kill any existing processes
pkill -f "uvicorn.*digital.*greenhouse" 2>/dev/null || true
pkill -f "npm.*run.*dev" 2>/dev/null || true
pkill -f "vite.*3000" 2>/dev/null || true

sleep 1

echo -e "${GREEN}✅ Ports cleared${NC}"
echo ""

# Start backend
echo -e "${PURPLE}🌿 Starting FastAPI Backend...${NC}"
cd backend

# Activate virtual environment
source venv/bin/activate

# Start backend server
echo -e "${GREEN}🚀 Backend starting on http://localhost:8000${NC}"
echo -e "${BLUE}   API Documentation: http://localhost:8000/docs${NC}"

# Use the run_dev.py script which handles initialization
python run_dev.py &
BACKEND_PID=$!

cd ..

# Wait for backend to initialize
echo -e "${BLUE}⏳ Waiting for backend to initialize...${NC}"
sleep 3

# Check if backend is responding
for i in {1..10}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${YELLOW}⚠️  Backend may still be initializing...${NC}"
    fi
    sleep 1
done

echo ""

# Start frontend
echo -e "${PURPLE}🎨 Starting React 3D Frontend...${NC}"
cd frontend

echo -e "${GREEN}🚀 Frontend starting on http://localhost:3000${NC}"
echo -e "${BLUE}   3D Garden Interface with hot reload${NC}"

npm run dev &
FRONTEND_PID=$!

cd ..

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down Digital Greenhouse...${NC}"
    
    # Kill processes gracefully
    if [[ -n "$FRONTEND_PID" ]]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    if [[ -n "$BACKEND_PID" ]]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    # Give processes time to clean up
    sleep 2
    
    # Force kill if needed
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}✅ Digital Greenhouse shut down cleanly${NC}"
    echo -e "${CYAN}Thanks for tending your digital garden! 🌱${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Wait for frontend to start
echo -e "${BLUE}⏳ Waiting for frontend to start...${NC}"
sleep 5

# Check if services are running
if check_port 8000 && check_port 3000; then
    echo ""
    echo -e "${GREEN}🌟 DIGITAL GREENHOUSE IS RUNNING! 🌟${NC}"
    echo ""
    echo -e "${CYAN}🌍 Your 3D Garden URLs:${NC}"
    echo -e "   ${GREEN}🎨 3D Garden Interface:${NC} http://localhost:3000"
    echo -e "   ${GREEN}⚡ API Backend:${NC}        http://localhost:8000"
    echo -e "   ${GREEN}📖 API Documentation:${NC}  http://localhost:8000/docs"
    echo ""
    echo -e "${CYAN}🌱 What you'll see:${NC}"
    echo -e "   • Interactive 3D garden with growing project plants"
    echo -e "   • Dynamic weather system with particle effects" 
    echo -e "   • Skill constellation you can navigate through"
    echo -e "   • Real-time growth based on sample data (or GitHub when configured)"
    echo -e "   • Beautiful glass morphism UI with seasonal themes"
    echo ""
    
    # Check GitHub configuration
    if grep -q "your_github_token_here" .env 2>/dev/null; then
        echo -e "${YELLOW}💡 Pro tip: Add your GitHub token to .env for real project data!${NC}"
        echo -e "${BLUE}   Currently using beautiful sample data to showcase the garden${NC}"
    else
        echo -e "${GREEN}🔗 GitHub integration active - your real projects are growing!${NC}"
    fi
    
    echo ""
    echo -e "${PURPLE}🎮 Garden Controls:${NC}"
    echo -e "   • Drag to rotate camera around the garden"
    echo -e "   • Click projects (plants) to view details" 
    echo -e "   • Use navigation overlay to switch views"
    echo -e "   • Watch for real-time weather and growth changes"
    echo ""
    echo -e "${CYAN}Press ${YELLOW}Ctrl+C${CYAN} to stop the garden${NC}"
    echo ""
    
    # Open browser automatically (macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${BLUE}🌐 Opening your digital garden in browser...${NC}"
        sleep 2
        open http://localhost:3000 2>/dev/null || true
    fi
    
else
    echo -e "${RED}❌ Services failed to start properly${NC}"
    echo -e "${YELLOW}Check the logs above for errors${NC}"
    cleanup
    exit 1
fi

# Monitor loop - keep script running and show status
while true; do
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Backend process died${NC}"
        cleanup
        exit 1
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Frontend process died${NC}"
        cleanup  
        exit 1
    fi
    
    sleep 10
done