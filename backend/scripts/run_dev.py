#!/usr/bin/env python3
"""
Development server runner for Digital Greenhouse API
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    """Run the development server"""
    
    # Set environment variables for development
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("LOG_LEVEL", "DEBUG")
    os.environ.setdefault("ENVIRONMENT", "development")
    
    # Check if .env file exists
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        print("⚠️  No .env file found. Copy .env.example to .env and configure your settings.")
        return 1
    
    # Run the development server
    try:
        print("🌱 Starting Digital Greenhouse API development server...")
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "debug"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Development server stopped")
        return 0
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())