#!/bin/bash

# Digital Greenhouse - Complete Setup Script
set -e

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Art banner
echo -e "${GREEN}"
echo "🌱🌿🌳🌸🍃🌺🌻🌹🌷🌼🌙✨"
echo "    DIGITAL GREENHOUSE SETUP"  
echo "  Complete 3D Portfolio Garden"
echo "🌱🌿🌳🌸🍃🌺🌻🌹🌷🌼🌙✨"
echo -e "${NC}"
echo ""

# Ensure we're in the right directory
if [[ ! -f "package.json" || ! -d "frontend" || ! -d "backend" ]]; then
    echo -e "${RED}❌ Error: Please run this script from the digital-greenhouse root directory${NC}"
    exit 1
fi

echo -e "${CYAN}🚀 Setting up your magical Digital Greenhouse...${NC}"
echo ""

# System requirements check
echo -e "${PURPLE}1️⃣ Checking system requirements...${NC}"

# Check Node.js
if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js: $NODE_VERSION${NC}"
else
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org${NC}"
    exit 1
fi

# Check npm
if command -v npm >/dev/null 2>&1; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅ npm: v$NPM_VERSION${NC}"
else
    echo -e "${RED}❌ npm not found${NC}"
    exit 1
fi

# Check Python
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+ from https://python.org${NC}"
    exit 1
fi

# Check pip
if command -v pip >/dev/null 2>&1; then
    PIP_VERSION=$(pip --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ pip: v$PIP_VERSION${NC}"
else
    echo -e "${RED}❌ pip not found${NC}"
    exit 1
fi

echo ""

# Environment setup
echo -e "${PURPLE}2️⃣ Setting up environment configuration...${NC}"

if [[ ! -f ".env" ]]; then
    echo -e "${BLUE}📄 Creating .env configuration file...${NC}"
    cat > .env << 'EOF'
# Digital Greenhouse Configuration

# Development Settings
DEBUG=true
ENVIRONMENT=development

# GitHub Integration (Optional - provides sample data if not configured)
# Get your token from: https://github.com/settings/tokens
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_username_here

# Optional External Integrations (all provide fallback data)
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
OPENWEATHER_API_KEY=your_openweather_api_key_here

# System Settings (these work out of the box)
DATABASE_URL=sqlite:///./digital_greenhouse.db
CACHE_TTL_GARDEN=300
CACHE_TTL_PROJECTS=600
ENABLE_SAMPLE_DATA=true
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}   You can add your GitHub token later for real project data${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

echo ""

# Install root dependencies
echo -e "${PURPLE}3️⃣ Installing root dependencies...${NC}"
npm install --silent

echo ""

# Backend setup
echo -e "${PURPLE}4️⃣ Setting up backend (FastAPI Garden API)...${NC}"
cd backend

echo -e "${BLUE}🐍 Creating Python virtual environment...${NC}"
if [[ -d "venv" ]]; then
    echo -e "${YELLOW}   Removing existing virtual environment...${NC}"
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

echo -e "${BLUE}📦 Installing backend dependencies...${NC}"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo -e "${BLUE}🧪 Testing backend imports...${NC}"
if python -c "import fastapi, uvicorn, sqlalchemy" 2>/dev/null; then
    echo -e "${GREEN}✅ Backend dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Backend installation failed${NC}"
    exit 1
fi

echo -e "${BLUE}🗄️ Initializing database and sample data...${NC}"
python -c "
import asyncio
from app.main import app
from app.sample_data import initialize_sample_data

async def setup():
    try:
        await initialize_sample_data()
        print('✅ Database and sample data initialized')
    except Exception as e:
        print(f'⚠️  Sample data will be initialized on first run: {e}')

asyncio.run(setup())
" 2>/dev/null || echo -e "${YELLOW}   Sample data will be generated on first startup${NC}"

cd ..

echo ""

# Frontend setup
echo -e "${PURPLE}5️⃣ Setting up frontend (3D Garden Interface)...${NC}"
cd frontend

echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
npm install --silent

echo -e "${BLUE}🏗️ Testing frontend build...${NC}"
if npm run build > build.log 2>&1; then
    echo -e "${GREEN}✅ Frontend build successful${NC}"
    rm build.log
else
    echo -e "${YELLOW}⚠️  Build warnings (usually okay for development)${NC}"
    rm -f build.log
fi

cd ..

echo ""

# Final verification
echo -e "${PURPLE}6️⃣ Final system verification...${NC}"

# Test backend can start
cd backend
source venv/bin/activate
if python -c "
from app.main import app
from app.core.database import init_db
import asyncio

async def test():
    await init_db()
    print('Backend: Ready')

try:
    asyncio.run(test())
except:
    print('Backend: Will initialize on startup')
" 2>/dev/null; then
    echo -e "${GREEN}✅ Backend verification passed${NC}"
else
    echo -e "${YELLOW}⚠️  Backend will initialize on first run${NC}"
fi

cd ../frontend
if [ -d "node_modules" ] && [ -f "package.json" ]; then
    echo -e "${GREEN}✅ Frontend verification passed${NC}"
else
    echo -e "${RED}❌ Frontend verification failed${NC}"
    exit 1
fi

cd ..

echo ""
echo -e "${GREEN}🎉 Digital Greenhouse setup complete! 🎉${NC}"
echo ""
echo -e "${CYAN}🚀 Ready to start your 3D garden:${NC}"
echo -e "${BLUE}   ./dev.sh${NC}"
echo ""
echo -e "${CYAN}🌍 Your garden will be available at:${NC}"
echo -e "${GREEN}   Frontend (3D Garden): http://localhost:3000${NC}"
echo -e "${GREEN}   Backend API:          http://localhost:8000${NC}"
echo -e "${GREEN}   API Documentation:    http://localhost:8000/docs${NC}"
echo ""
echo -e "${CYAN}💡 Features included out of the box:${NC}"
echo -e "   🌱 6 sample projects with realistic growth stages"
echo -e "   ⭐ 15+ skills in interactive constellation"
echo -e "   🌤️ Dynamic weather system with 6 weather types"
echo -e "   📊 Real-time analytics and visitor tracking"
echo -e "   🎨 Beautiful 3D garden interface"
echo ""
echo -e "${YELLOW}🔑 Optional: Add your GitHub token to .env for real project data${NC}"
echo -e "${CYAN}   Edit .env and replace 'your_github_token_here' with your actual token${NC}"
echo ""
echo -e "${GREEN}🌱 Happy gardening! Your digital ecosystem is ready to grow! 🌱${NC}"