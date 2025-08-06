"""
Sample data system for Digital Greenhouse API
Provides realistic demo data when GitHub integration isn't configured
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import AsyncSessionLocal
from app.models.projects import Project, ProjectGrowthLog
from app.schemas.projects import GrowthStage, PlantType
from app.models.skills import Skill
from app.schemas.skills import SkillCategory
from app.models.weather import WeatherState
from app.schemas.weather import WeatherType
from app.models.visitors import VisitorSession

logger = logging.getLogger(__name__)

class SampleDataGenerator:
    """Generate comprehensive sample data for the Digital Greenhouse"""
    
    def __init__(self):
        self.sample_projects = [
            {
                "name": "Digital Greenhouse",
                "description": "Interactive 3D portfolio showcasing projects as plants in a virtual garden",
                "category": "web-development",
                "technologies": ["React", "Three.js", "FastAPI", "SQLite", "Python"],
                "github_url": "https://github.com/cameronopotter/digital-greenhouse",
                "live_url": "https://greenhouse.cameronpotter.dev",
                "growth_stage": GrowthStage.MATURE,
                "plant_type": PlantType.TREE,
                "position_x": 0.0,
                "position_y": 0.0,
                "position_z": 0.0,
                "commits": 250,
                "stars": 45,
                "watchers": 12,
                "last_activity": datetime.now() - timedelta(days=2),
                "health_score": 0.95
            },
            {
                "name": "AI Chat Assistant",
                "description": "Intelligent conversational AI built with modern NLP techniques",
                "category": "machine-learning",
                "technologies": ["Python", "TensorFlow", "Transformers", "FastAPI", "Docker"],
                "github_url": "https://github.com/cameronopotter/ai-chat-assistant",
                "live_url": "https://chat.cameronpotter.dev",
                "growth_stage": GrowthStage.GROWING,
                "plant_type": PlantType.FLOWER,
                "position_x": 5.0,
                "position_y": 0.0,
                "position_z": 3.0,
                "commits": 180,
                "stars": 28,
                "watchers": 7,
                "last_activity": datetime.now() - timedelta(days=1),
                "health_score": 0.88
            },
            {
                "name": "E-commerce Platform",
                "description": "Full-stack e-commerce solution with modern payment integration",
                "category": "web-development",
                "technologies": ["Next.js", "PostgreSQL", "Stripe", "Redis", "TypeScript"],
                "github_url": "https://github.com/cameronopotter/ecommerce-platform",
                "live_url": "https://shop.example.com",
                "growth_stage": GrowthStage.GROWING,
                "plant_type": PlantType.TREE,
                "position_x": -4.0,
                "position_y": 0.0,
                "position_z": 2.0,
                "commits": 120,
                "stars": 15,
                "watchers": 4,
                "last_activity": datetime.now() - timedelta(days=5),
                "health_score": 0.82
            },
            {
                "name": "Mobile Game Engine",
                "description": "Cross-platform mobile game engine with physics simulation",
                "category": "game-development",
                "technologies": ["Unity", "C#", "Firebase", "iOS", "Android"],
                "github_url": "https://github.com/cameronopotter/mobile-game-engine",
                "live_url": None,
                "growth_stage": GrowthStage.SPROUT,
                "plant_type": PlantType.FLOWER,
                "position_x": 3.0,
                "position_y": 0.0,
                "position_z": -2.0,
                "commits": 85,
                "stars": 8,
                "watchers": 3,
                "last_activity": datetime.now() - timedelta(days=7),
                "health_score": 0.75
            },
            {
                "name": "Data Visualization Toolkit",
                "description": "Interactive data visualization library for complex datasets",
                "category": "data-science",
                "technologies": ["D3.js", "Python", "Jupyter", "Pandas", "NumPy"],
                "github_url": "https://github.com/cameronopotter/data-viz-toolkit",
                "live_url": "https://dataviz.cameronpotter.dev",
                "growth_stage": GrowthStage.BLOOMING,
                "plant_type": PlantType.SHRUB,
                "position_x": -2.0,
                "position_y": 0.0,
                "position_z": -4.0,
                "commits": 45,
                "stars": 5,
                "watchers": 2,
                "last_activity": datetime.now() - timedelta(days=10),
                "health_score": 0.68
            },
            {
                "name": "Blockchain Explorer",
                "description": "Real-time blockchain transaction explorer and analytics platform",
                "category": "blockchain",
                "technologies": ["Web3.js", "Ethereum", "React", "GraphQL", "Node.js"],
                "github_url": "https://github.com/cameronopotter/blockchain-explorer",
                "live_url": None,
                "growth_stage": GrowthStage.SEED,
                "plant_type": PlantType.HERB,
                "position_x": 1.0,
                "position_y": 0.0,
                "position_z": 5.0,
                "commits": 20,
                "stars": 2,
                "watchers": 1,
                "last_activity": datetime.now() - timedelta(days=15),
                "health_score": 0.60
            }
        ]
        
        self.sample_skills = [
            # Programming Languages
            {
                "name": "Python",
                "category": SkillCategory.BACKEND,
                "proficiency": 0.95,
                "position_x": 2.0,
                "position_y": 1.0,
                "position_z": 1.0,
                "projects_count": 4,
                "years_experience": 8
            },
            {
                "name": "JavaScript",
                "category": SkillCategory.BACKEND,
                "proficiency": 0.92,
                "position_x": -1.5,
                "position_y": 0.8,
                "position_z": 2.5,
                "projects_count": 5,
                "years_experience": 7
            },
            {
                "name": "TypeScript",
                "category": SkillCategory.BACKEND,
                "proficiency": 0.88,
                "position_x": 0.5,
                "position_y": 1.2,
                "position_z": -1.0,
                "projects_count": 3,
                "years_experience": 5
            },
            {
                "name": "C#",
                "category": SkillCategory.BACKEND,
                "proficiency": 0.75,
                "position_x": -2.0,
                "position_y": 0.9,
                "position_z": -2.0,
                "projects_count": 2,
                "years_experience": 4
            },
            # Frameworks & Libraries
            {
                "name": "React",
                "category": SkillCategory.FRONTEND,
                "proficiency": 0.90,
                "position_x": 3.0,
                "position_y": 0.6,
                "position_z": 0.5,
                "projects_count": 4,
                "years_experience": 6
            },
            {
                "name": "FastAPI",
                "category": SkillCategory.FRONTEND,
                "proficiency": 0.85,
                "position_x": 1.8,
                "position_y": 0.7,
                "position_z": 3.0,
                "projects_count": 3,
                "years_experience": 3
            },
            {
                "name": "Three.js",
                "category": SkillCategory.FRONTEND,
                "proficiency": 0.80,
                "position_x": -0.5,
                "position_y": 1.1,
                "position_z": 1.5,
                "projects_count": 2,
                "years_experience": 2
            },
            {
                "name": "Next.js",
                "category": SkillCategory.FRONTEND,
                "proficiency": 0.78,
                "position_x": -3.0,
                "position_y": 0.8,
                "position_z": 0.8,
                "projects_count": 2,
                "years_experience": 3
            },
            # Tools & Technologies
            {
                "name": "Docker",
                "category": SkillCategory.DEVOPS,
                "proficiency": 0.85,
                "position_x": 2.5,
                "position_y": -0.2,
                "position_z": -1.5,
                "projects_count": 4,
                "years_experience": 5
            },
            {
                "name": "Git",
                "category": SkillCategory.DEVOPS,
                "proficiency": 0.95,
                "position_x": 0.2,
                "position_y": -0.1,
                "position_z": 2.8,
                "projects_count": 6,
                "years_experience": 8
            },
            {
                "name": "PostgreSQL",
                "category": SkillCategory.BACKEND,
                "proficiency": 0.80,
                "position_x": -1.8,
                "position_y": -0.3,
                "position_z": -0.5,
                "projects_count": 3,
                "years_experience": 4
            },
            {
                "name": "Redis",
                "category": SkillCategory.BACKEND,
                "proficiency": 0.70,
                "position_x": 1.2,
                "position_y": -0.4,
                "position_z": 0.8,
                "projects_count": 2,
                "years_experience": 3
            },
            # Soft Skills
            {
                "name": "Problem Solving",
                "category": SkillCategory.GENERAL,
                "proficiency": 0.92,
                "position_x": 0.0,
                "position_y": 2.0,
                "position_z": 0.0,
                "projects_count": 6,
                "years_experience": 10
            },
            {
                "name": "Team Leadership",
                "category": SkillCategory.GENERAL,
                "proficiency": 0.85,
                "position_x": -1.0,
                "position_y": 1.8,
                "position_z": 1.5,
                "projects_count": 4,
                "years_experience": 6
            },
            {
                "name": "Communication",
                "category": SkillCategory.GENERAL,
                "proficiency": 0.88,
                "position_x": 1.5,
                "position_y": 1.9,
                "position_z": -0.8,
                "projects_count": 6,
                "years_experience": 8
            }
        ]

    async def create_sample_projects(self, session: AsyncSession) -> List[Project]:
        """Create sample projects in the database"""
        projects = []
        
        for project_data in self.sample_projects:
            project = Project(
                name=project_data["name"],
                description=project_data["description"],
                technologies=str(project_data["technologies"]).replace("'", '"'),  # Convert to JSON string
                github_repo=project_data["github_url"],
                demo_url=project_data.get("live_url"),
                growth_stage=project_data["growth_stage"].value,
                plant_type=project_data["plant_type"].value,
                position_x=project_data["position_x"],
                position_y=project_data["position_y"],
                position_z=project_data["position_z"],
                commit_count=project_data["commits"],
                visitor_interactions=project_data["stars"] + project_data["watchers"],  # Combine as interactions
                status='featured' if project_data["name"] == "Digital Greenhouse" else 'active'
            )
            session.add(project)
            projects.append(project)
        
        await session.flush()  # Get IDs
        return projects

    async def create_sample_growth_logs(self, session: AsyncSession, projects: List[Project]):
        """Create realistic growth history for projects"""
        for project in projects:
            # Create growth stages progression
            base_date = datetime.now() - timedelta(days=365)  # Start a year ago
            
            stages = [GrowthStage.SEED, GrowthStage.SPROUT, GrowthStage.GROWING, GrowthStage.BLOOMING, GrowthStage.MATURE]
            current_stage_index = stages.index(project.growth_stage)
            
            for i in range(current_stage_index + 1):
                stage = stages[i]
                log_date = base_date + timedelta(days=i * 90 + (len(project.name) * 2))  # Stagger dates
                
                growth_log = ProjectGrowthLog(
                    project_id=project.id,
                    previous_stage=stages[i-1].value if i > 0 else None,
                    new_stage=stage.value,
                    commits_delta=(i + 1) * 30,
                    lines_added=(i + 1) * 100,
                    complexity_change=(i + 1) * 0.1,
                    page_views=(i + 1) * 50,
                    interactions=(i + 1) * 10,
                    growth_factor=min(1.0, (i + 1) * 0.2),
                    recorded_at=log_date
                )
                session.add(growth_log)

    async def create_sample_skills(self, session: AsyncSession) -> List[Skill]:
        """Create sample skills in the database"""
        skills = []
        
        for skill_data in self.sample_skills:
            skill = Skill(
                name=skill_data["name"],
                category=skill_data["category"].value,
                proficiency_level=int(skill_data["proficiency"] * 10),  # Convert 0.95 to 9
                position_x=skill_data["position_x"],
                position_y=skill_data["position_y"],
                brightness=skill_data["proficiency"],  # Use proficiency as brightness
                projects_used_in=skill_data["projects_count"],
                hours_practiced=skill_data["years_experience"] * 365,  # Approximate hours
                last_used_date=datetime.now().date() - timedelta(days=7)
            )
            session.add(skill)
            skills.append(skill)
        
        return skills

    async def create_sample_weather_history(self, session: AsyncSession):
        """Create realistic weather pattern history"""
        weather_types = [
            WeatherType.SUNNY,
            WeatherType.CLOUDY,
            WeatherType.STORMY,
            WeatherType.MISTY,
            WeatherType.STARRY,
            WeatherType.AURORA
        ]
        
        current_date = datetime.now() - timedelta(days=30)  # Start 30 days ago
        
        for i in range(30):  # Create 30 days of weather history
            weather_type = weather_types[i % len(weather_types)]
            weather_date = current_date + timedelta(days=i)
            
            # Don't create weather for today (current weather)
            if weather_date.date() == datetime.now().date():
                continue
            
            weather_state = WeatherState(
                weather_type=weather_type.value,
                intensity=0.5 + (i % 5) * 0.1,  # Vary between 0.5-0.9
                github_commits_today=i % 10,  # Vary commits
                coding_hours_today=float(i % 8),  # Vary hours 0-7
                music_mood="focused" if i % 3 == 0 else "calm",
                actual_weather="clear" if i % 2 == 0 else "cloudy",
                productivity_score=0.6 + (i % 4) * 0.1,
                creativity_index=0.5 + (i % 5) * 0.1,
                stress_level=0.2 + (i % 3) * 0.1,
                time_of_day="day" if i % 4 < 2 else "night",
                season="spring" if i % 4 == 0 else "summer",
                started_at=weather_date,
                ended_at=weather_date + timedelta(hours=23, minutes=59)
            )
            session.add(weather_state)
        
        # Create current weather
        current_weather = WeatherState(
            weather_type=WeatherType.SUNNY.value,
            intensity=0.8,
            github_commits_today=5,
            coding_hours_today=3.5,
            music_mood="energetic",
            actual_weather="clear",
            productivity_score=0.9,
            creativity_index=0.8,
            stress_level=0.15,
            time_of_day="day",
            season="summer",
            started_at=datetime.now()
        )
        session.add(current_weather)

    async def create_sample_visitor_data(self, session: AsyncSession):
        """Create sample visitor interactions"""
        # Create some sample visitor sessions from the past week
        for i in range(10):
            session_date = datetime.now() - timedelta(days=i, hours=i*2)
            
            visitor_session = VisitorSession(
                session_token=f"demo_visitor_{i:03d}",
                user_agent="Mozilla/5.0 (Demo Browser)",
                ip_hash=f"hash_{i:03d}",
                country_code="US",
                entry_point="https://github.com/cameronopotter" if i % 3 == 0 else "direct",
                total_time_seconds=15 * 60 + i * 5 * 60,  # 15-65 minutes
                clicks_count=10 + i * 2,
                seeds_planted=i % 3,
                device_type="desktop",
                browser="Chrome",
                screen_resolution="1920x1080",
                started_at=session_date,
                last_activity_at=session_date + timedelta(minutes=15 + i*5)
            )
            session.add(visitor_session)

    async def clear_existing_data(self, session: AsyncSession):
        """Clear existing sample data"""
        logger.info("Clearing existing sample data...")
        
        # Delete in correct order due to foreign key constraints
        await session.execute(delete(VisitorSession))
        await session.execute(delete(ProjectGrowthLog))
        await session.execute(delete(WeatherState))
        await session.execute(delete(Skill))
        await session.execute(delete(Project))
        
        await session.commit()

    async def generate_all_sample_data(self, session: Optional[AsyncSession] = None):
        """Generate complete sample dataset"""
        if session is None:
            async with AsyncSessionLocal() as session:
                return await self._generate_sample_data_impl(session)
        else:
            return await self._generate_sample_data_impl(session)

    async def _generate_sample_data_impl(self, session: AsyncSession):
        """Internal implementation of sample data generation"""
        try:
            logger.info("Starting sample data generation...")
            
            # Clear existing data first
            await self.clear_existing_data(session)
            
            # Create projects and get their IDs
            projects = await self.create_sample_projects(session)
            await session.commit()
            
            # Refresh projects to get IDs
            for project in projects:
                await session.refresh(project)
            
            # Create growth logs
            await self.create_sample_growth_logs(session, projects)
            
            # Create skills
            skills = await self.create_sample_skills(session)
            
            # Create weather history
            await self.create_sample_weather_history(session)
            
            # Create visitor data
            await self.create_sample_visitor_data(session)
            
            await session.commit()
            
            logger.info(f"Sample data generation completed successfully!")
            logger.info(f"Created {len(projects)} projects, {len(skills)} skills, weather history, and visitor data")
            
            return {
                "projects": len(projects),
                "skills": len(skills),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating sample data: {e}")
            await session.rollback()
            raise


# Global instance
sample_data_generator = SampleDataGenerator()


async def init_sample_data():
    """Initialize sample data if no data exists"""
    async with AsyncSessionLocal() as session:
        # Check if we have any projects
        result = await session.execute(select(Project).limit(1))
        existing_project = result.scalar_one_or_none()
        
        if not existing_project:
            logger.info("No existing data found, generating sample data...")
            await sample_data_generator.generate_all_sample_data(session)
        else:
            logger.info("Existing data found, skipping sample data generation")


async def refresh_sample_data():
    """Refresh all sample data (admin function)"""
    logger.info("Refreshing sample data...")
    async with AsyncSessionLocal() as session:
        return await sample_data_generator.generate_all_sample_data(session)