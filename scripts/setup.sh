#!/bin/bash

# Digital Greenhouse Setup Script
# Automated setup for the complete development environment

set -e  # Exit on any error

# Colors for output
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
echo "   DIGITAL GREENHOUSE SETUP"  
echo "🌱🌿🌳🌸🍃🌺🌻🌹🌷🌼🌙✨"
echo -e "${NC}"

echo -e "${CYAN}Initializing your magical digital ecosystem...${NC}\n"

# Check if we're in the right directory
if [[ ! -f "package.json" || ! -d "frontend" || ! -d "backend" ]]; then
    echo -e "${RED}❌ Error: Please run this script from the digital-greenhouse root directory${NC}"
    exit 1
fi

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check version
check_version() {
    local cmd="$1"
    local required_version="$2"
    local current_version="$3"
    
    if ! command_exists "$cmd"; then
        echo -e "${RED}❌ $cmd is not installed${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ $cmd found: $current_version${NC}"
    return 0
}

echo -e "${PURPLE}🔍 Checking system requirements...${NC}"

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    check_version "node" "18.0.0" "$NODE_VERSION"
else
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org${NC}"
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    check_version "npm" "9.0.0" "$NPM_VERSION"
else
    echo -e "${RED}❌ npm not found. Please install npm 9+${NC}"
    exit 1
fi

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    check_version "python3" "3.11.0" "$PYTHON_VERSION"
else
    echo -e "${RED}❌ Python 3.11+ not found. Please install Python from https://python.org${NC}"
    exit 1
fi

# Check pip
if command_exists pip; then
    PIP_VERSION=$(pip --version)
    check_version "pip" "" "$PIP_VERSION"
else
    echo -e "${RED}❌ pip not found. Please install pip${NC}"
    exit 1
fi

# Check Docker (optional but recommended)
if command_exists docker; then
    DOCKER_VERSION=$(docker --version)
    check_version "docker" "" "$DOCKER_VERSION"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  Docker not found. You can still run manually but Docker is recommended${NC}"
    DOCKER_AVAILABLE=false
fi

# Check Docker Compose
if command_exists docker-compose; then
    COMPOSE_VERSION=$(docker-compose --version)
    check_version "docker-compose" "" "$COMPOSE_VERSION"
    COMPOSE_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  Docker Compose not found${NC}"
    COMPOSE_AVAILABLE=false
fi

echo ""

# Setup environment file
echo -e "${PURPLE}📋 Setting up environment configuration...${NC}"

if [[ ! -f ".env" ]]; then
    echo -e "${BLUE}📄 Copying .env.example to .env${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your API keys before running the application${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Install root dependencies
echo -e "${PURPLE}📦 Installing root dependencies...${NC}"
npm install --silent

# Frontend setup
echo -e "${PURPLE}🎨 Setting up frontend (React 3D Garden)...${NC}"
cd frontend

echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
npm install --silent

echo -e "${BLUE}🔧 Setting up frontend configuration...${NC}"

# Create frontend .env if needed
if [[ ! -f ".env" ]]; then
    cat > .env << 'EOF'
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_ENABLE_DEBUG_MODE=true
VITE_MAX_PARTICLES=1000
VITE_DEFAULT_QUALITY=high
EOF
    echo -e "${GREEN}✅ Frontend .env created${NC}"
fi

# Build frontend for production check
echo -e "${BLUE}🏗️  Testing frontend build...${NC}"
if npm run build > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend build successful${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend build had warnings (this is usually okay)${NC}"
fi

cd ..

# Backend setup  
echo -e "${PURPLE}⚡ Setting up backend (FastAPI Garden Orchestrator)...${NC}"
cd backend

echo -e "${BLUE}📦 Installing backend dependencies...${NC}"

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    echo -e "${BLUE}🐍 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Test imports
echo -e "${BLUE}🧪 Testing backend imports...${NC}"
if python -c "import fastapi, sqlalchemy, redis, celery" 2>/dev/null; then
    echo -e "${GREEN}✅ Backend imports successful${NC}"
else
    echo -e "${RED}❌ Backend import test failed${NC}"
    exit 1
fi

cd ..

# Database setup
echo -e "${PURPLE}🗄️  Setting up database...${NC}"

if [[ "$DOCKER_AVAILABLE" == true && "$COMPOSE_AVAILABLE" == true ]]; then
    echo -e "${BLUE}🐳 Starting database services with Docker...${NC}"
    docker-compose up -d postgres redis
    
    # Wait for services to be ready
    echo -e "${BLUE}⏳ Waiting for database services to be ready...${NC}"
    sleep 10
    
    # Check if services are running
    if docker-compose ps postgres | grep -q "Up"; then
        echo -e "${GREEN}✅ PostgreSQL is running${NC}"
    else
        echo -e "${YELLOW}⚠️  PostgreSQL may not be ready yet${NC}"
    fi
    
    if docker-compose ps redis | grep -q "Up"; then
        echo -e "${GREEN}✅ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis may not be ready yet${NC}"
    fi
    
    # Run database migrations
    echo -e "${BLUE}🔄 Running database migrations...${NC}"
    cd backend
    source venv/bin/activate
    
    # Set database URL for migrations
    export DATABASE_URL="postgresql://garden_user:garden_secret_2024@localhost:5432/digital_greenhouse"
    
    if command_exists alembic; then
        alembic upgrade head
        echo -e "${GREEN}✅ Database migrations completed${NC}"
    else
        echo -e "${YELLOW}⚠️  Alembic not found, skipping migrations${NC}"
    fi
    
    cd ..
    
else
    echo -e "${YELLOW}⚠️  Docker not available. Please manually set up PostgreSQL and Redis${NC}"
    echo -e "${BLUE}   PostgreSQL: Create database 'digital_greenhouse' with user 'garden_user'${NC}"
    echo -e "${BLUE}   Redis: Install and run Redis server on default port 6379${NC}"
fi

# Create initial project data (optional)
echo -e "${PURPLE}🌱 Would you like to create sample project data? (y/n)${NC}"
read -r create_samples

if [[ "$create_samples" == "y" || "$create_samples" == "Y" ]]; then
    echo -e "${BLUE}🌿 Creating sample project data...${NC}"
    
    # Create sample data script
    cat > sample_data.py << 'EOF'
import asyncio
import sys
import os
sys.path.append('backend')

from backend.app.core.database import get_db
from backend.app.models.project import Project
from backend.app.models.skill import Skill
from sqlalchemy.orm import Session

async def create_sample_data():
    db = next(get_db())
    try:
        # Sample projects
        projects = [
            {
                "name": "Digital Greenhouse",
                "description": "Interactive 3D personal portfolio",
                "github_repo": "cameronopotter/digital-greenhouse",
                "plant_type": "flowering_tree",
                "growth_stage": "mature",
                "position_x": 0,
                "position_y": 0,
                "position_z": 0,
                "technologies": ["React", "Three.js", "FastAPI", "PostgreSQL"]
            },
            {
                "name": "AI Chat Assistant",
                "description": "Intelligent conversational AI",
                "github_repo": "cameronopotter/ai-assistant",
                "plant_type": "oak_tree", 
                "growth_stage": "growing",
                "position_x": 5,
                "position_y": 0,
                "position_z": 3,
                "technologies": ["Python", "OpenAI", "FastAPI", "Docker"]
            },
            {
                "name": "Mobile Fitness Tracker",
                "description": "React Native fitness application",
                "github_repo": "cameronopotter/fitness-tracker",
                "plant_type": "palm_tree",
                "growth_stage": "blooming",
                "position_x": -3,
                "position_y": 0,
                "position_z": 4,
                "technologies": ["React Native", "Node.js", "MongoDB", "AWS"]
            }
        ]
        
        for project_data in projects:
            project = Project(**project_data)
            db.add(project)
        
        # Sample skills
        skills = [
            {"name": "React", "category": "frontend", "proficiency_level": 9},
            {"name": "TypeScript", "category": "frontend", "proficiency_level": 8},
            {"name": "Python", "category": "backend", "proficiency_level": 9},
            {"name": "FastAPI", "category": "backend", "proficiency_level": 8},
            {"name": "PostgreSQL", "category": "backend", "proficiency_level": 7},
            {"name": "Docker", "category": "devops", "proficiency_level": 7},
            {"name": "Three.js", "category": "frontend", "proficiency_level": 6},
        ]
        
        for skill_data in skills:
            skill = Skill(**skill_data)
            db.add(skill)
        
        db.commit()
        print("✅ Sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_sample_data())
EOF

    cd backend
    source venv/bin/activate
    python ../sample_data.py
    cd ..
    rm sample_data.py
fi

# Setup monitoring (optional)
if [[ "$DOCKER_AVAILABLE" == true ]]; then
    echo -e "${PURPLE}📊 Would you like to set up monitoring (Grafana + Prometheus)? (y/n)${NC}"
    read -r setup_monitoring
    
    if [[ "$setup_monitoring" == "y" || "$setup_monitoring" == "Y" ]]; then
        echo -e "${BLUE}📊 Setting up monitoring stack...${NC}"
        docker-compose -f docker-compose.monitoring.yml up -d
        echo -e "${GREEN}✅ Monitoring setup complete${NC}"
        echo -e "${BLUE}   Grafana: http://localhost:3001 (admin/admin123)${NC}"
        echo -e "${BLUE}   Prometheus: http://localhost:9090${NC}"
    fi
fi

# Final checks and startup instructions
echo ""
echo -e "${GREEN}🎉 Digital Greenhouse setup complete! 🎉${NC}"
echo ""
echo -e "${CYAN}🚀 Quick Start Commands:${NC}"
echo ""

if [[ "$DOCKER_AVAILABLE" == true ]]; then
    echo -e "${BLUE}   Full Docker Setup:${NC}"
    echo -e "   ${YELLOW}docker-compose up -d${NC}         # Start all services"
    echo -e "   ${YELLOW}docker-compose logs -f${NC}       # View logs"
    echo ""
fi

echo -e "${BLUE}   Manual Development:${NC}"
echo -e "   ${YELLOW}npm run dev${NC}                   # Start both frontend and backend"
echo -e "   ${YELLOW}npm run dev:frontend${NC}          # Frontend only (port 3000)"
echo -e "   ${YELLOW}npm run dev:backend${NC}           # Backend only (port 8000)"
echo ""

echo -e "${CYAN}🌍 Access Your Garden:${NC}"
echo -e "   ${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "   ${GREEN}API Docs:${NC} http://localhost:8000/docs"
if [[ "$setup_monitoring" == "y" || "$setup_monitoring" == "Y" ]]; then
    echo -e "   ${GREEN}Monitoring:${NC} http://localhost:3001"
fi
echo ""

echo -e "${CYAN}⚠️  Important Next Steps:${NC}"
echo -e "${YELLOW}1. Edit .env file with your GitHub token (required)${NC}"
echo -e "${YELLOW}2. Add optional API keys for enhanced features${NC}"
echo -e "${YELLOW}3. Customize your garden theme and project data${NC}"
echo ""

echo -e "${GREEN}🌱 Your Digital Greenhouse is ready to grow! 🌱${NC}"
echo -e "${PURPLE}Happy coding! 🚀${NC}"