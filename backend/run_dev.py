#!/usr/bin/env python3
"""
Simple development server runner for Digital Greenhouse API
"""

import os
import sys
import logging
import uvicorn
from pathlib import Path

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables for development
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("SECRET_KEY", "development-secret-key-change-in-production-123456789")
os.environ.setdefault("ADMIN_PASSWORD", "admin123")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    print("🌱 Starting Digital Greenhouse API Development Server...")
    print("🔧 Configuration:")
    print("   - Database: SQLite (digital_greenhouse.db)")
    print("   - Cache: In-memory")
    print("   - Background Tasks: Asyncio")
    print("   - Sample Data: Auto-generated if no data exists")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Health Check: http://localhost:8000/health")
    print("\n💡 Admin endpoints available:")
    print("   - POST /admin/tasks/growth-calculation")
    print("   - POST /admin/tasks/weather-update")
    print("   - POST /admin/tasks/data-sync")
    print("   - POST /admin/sample-data/refresh")
    print("\n🚀 Starting server...")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )