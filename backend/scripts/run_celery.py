#!/usr/bin/env python3
"""
Celery worker/beat runner for Digital Greenhouse API
"""

import os
import subprocess
import sys
import argparse
from pathlib import Path

def run_worker():
    """Run Celery worker"""
    print("🌱 Starting Celery worker...")
    subprocess.run([
        "celery", "-A", "app.tasks.celery_app", 
        "worker", 
        "--loglevel=info",
        "--concurrency=2",
        "--queues=growth,sync,maintenance"
    ], check=True)

def run_beat():
    """Run Celery beat scheduler"""
    print("⏰ Starting Celery beat scheduler...")
    subprocess.run([
        "celery", "-A", "app.tasks.celery_app",
        "beat",
        "--loglevel=info"
    ], check=True)

def run_flower():
    """Run Flower monitoring dashboard"""
    print("🌸 Starting Flower monitoring dashboard...")
    subprocess.run([
        "celery", "-A", "app.tasks.celery_app",
        "flower",
        "--port=5555"
    ], check=True)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run Celery components")
    parser.add_argument(
        "component", 
        choices=["worker", "beat", "flower"],
        help="Component to run"
    )
    
    args = parser.parse_args()
    
    # Check if .env file exists
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        print("⚠️  No .env file found. Copy .env.example to .env and configure your settings.")
        return 1
    
    try:
        if args.component == "worker":
            run_worker()
        elif args.component == "beat":
            run_beat()
        elif args.component == "flower":
            run_flower()
            
    except KeyboardInterrupt:
        print(f"\n👋 {args.component} stopped")
        return 0
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {args.component}: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())