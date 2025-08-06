#!/usr/bin/env python3
"""
Quick start script for the project orchestrator
"""

import asyncio
import sys
from orchestrator import Orchestrator

async def main():
    print("🚀 Starting Project Orchestrator...")
    print("=" * 50)
    
    orchestrator = Orchestrator()
    
    # Display initial status
    status = await orchestrator.get_overall_status()
    print(f"📊 Overall Progress: {status['overall_completion']:.1f}%")
    print(f"🎨 Frontend: {status['frontend']['completion']:.1f}%")
    print(f"⚡ Backend: {status['backend']['completion']:.1f}%")
    print("=" * 50)
    
    try:
        print("⏰ Orchestrator will check in every hour...")
        print("Press Ctrl+C to stop")
        await orchestrator.start_orchestration()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down orchestrator...")
        orchestrator.stop_orchestration()
    except Exception as e:
        print(f"❌ Error: {e}")
        orchestrator.stop_orchestration()

if __name__ == "__main__":
    asyncio.run(main())