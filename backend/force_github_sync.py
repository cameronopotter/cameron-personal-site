#!/usr/bin/env python3
"""
Force GitHub Sync Script
Clears sample data and replaces it with real GitHub projects
"""

import asyncio
import logging
import sys
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv("/Users/cameronopotter/Documents/Personal/digital-greenhouse/.env")
load_dotenv("/Users/cameronopotter/Documents/Personal/digital-greenhouse/backend/.env")

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.core.database import AsyncSessionLocal, init_database
from app.sample_data import sample_data_generator
from app.integrations.github_service import GitHubService
from app.background_tasks import task_manager
from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def force_github_sync():
    """Force clear sample data and sync GitHub projects"""
    
    # Check configuration
    if not settings.enable_github_integration:
        logger.error("❌ GitHub integration is disabled. Set enable_github_integration=True in config.")
        return False
    
    if not settings.github_token or not settings.github_username:
        logger.error("❌ GitHub credentials not configured. Set GITHUB_TOKEN and GITHUB_USERNAME in .env file.")
        logger.error(f"   Current GITHUB_TOKEN: {'SET' if settings.github_token else 'NOT SET'}")
        logger.error(f"   Current GITHUB_USERNAME: {settings.github_username or 'NOT SET'}")
        return False
    
    logger.info(f"🔧 GitHub Config: {settings.github_username}, Token: {'SET' if settings.github_token else 'NOT SET'}")
    
    async with AsyncSessionLocal() as session:
        try:
            # Step 1: Clear existing data
            logger.info("🧹 Step 1: Clearing all existing sample/project data...")
            await sample_data_generator.clear_existing_data(session)
            logger.info("✅ Successfully cleared existing data")
            
            # Step 2: Sync GitHub repositories
            logger.info("🔄 Step 2: Fetching GitHub repositories...")
            github_service = GitHubService()
            sync_result = await github_service.sync_all_repositories()
            
            if not sync_result.get("success", False):
                logger.error(f"❌ GitHub sync failed: {sync_result.get('error', 'Unknown error')}")
                return False
            
            repositories = sync_result.get("repositories", [])
            logger.info(f"✅ Successfully fetched {len(repositories)} repositories from GitHub")
            
            # Step 3: Create Project records
            logger.info("💾 Step 3: Creating Project records from GitHub data...")
            updated_projects = await task_manager._create_projects_from_github_data(session, repositories)
            
            logger.info("🎉 SYNC COMPLETE!")
            logger.info(f"   📊 Repositories synced: {len(repositories)}")
            logger.info(f"   🌱 Projects created: {updated_projects}")
            logger.info(f"   📚 Repository names: {[repo['name'] for repo in repositories]}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during GitHub sync: {e}")
            import traceback
            traceback.print_exc()
            return False


async def check_current_projects():
    """Check what projects are currently in the database"""
    from sqlalchemy import select
    from app.models.projects import Project
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Project))
        projects = result.scalars().all()
        
        if not projects:
            logger.info("📭 No projects found in database")
        else:
            logger.info(f"📋 Found {len(projects)} projects in database:")
            for project in projects:
                logger.info(f"   - {project.name} ({project.github_repo or 'no github repo'})")


async def main():
    """Main function"""
    logger.info("🌱 Digital Greenhouse - Force GitHub Sync Tool")
    logger.info("=" * 50)
    
    # Initialize database first
    logger.info("🔧 Initializing database...")
    try:
        await init_database()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        return
    
    # Check current state
    logger.info("🔍 Checking current projects in database...")
    await check_current_projects()
    
    # For automated execution, skip confirmation
    # Confirm action  
    logger.info("⚠️  This will CLEAR ALL existing projects and replace them with GitHub data.")
    logger.info("🚀 Proceeding automatically...")
    
    # Uncomment below for interactive mode:
    # print("\n⚠️  This will CLEAR ALL existing projects and replace them with GitHub data.")
    # response = input("Continue? (y/N): ")
    # if response.lower() != 'y':
    #     logger.info("❌ Operation cancelled by user")
    #     return
    
    # Force sync
    success = await force_github_sync()
    
    if success:
        logger.info("\n🔍 Checking updated projects...")
        await check_current_projects()
        logger.info("\n✅ SUCCESS: Real GitHub projects should now appear in the Digital Greenhouse!")
    else:
        logger.error("\n❌ FAILED: Could not sync GitHub data. Check logs above for details.")


if __name__ == "__main__":
    asyncio.run(main())