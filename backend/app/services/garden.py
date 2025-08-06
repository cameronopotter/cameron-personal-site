"""
Garden ecosystem service for managing the overall garden state
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from uuid import UUID

from app.models.projects import Project, ProjectGrowthLog
from app.models.skills import Skill, SkillConnection
from app.models.weather import WeatherState
from app.models.visitors import VisitorSession
from app.schemas.garden import (
    GardenState, GardenSummaryResponse, GardenEvolution,
    GardenInteractionSuggestion, GardenHealth
)
from app.schemas.projects import (
    ProjectResponse, SeedPlantingRequest, PlantedSeedResponse, GrowthStage
)
from app.schemas.skills import SkillResponse, ConstellationResponse
from app.schemas.weather import WeatherStateResponse
from app.services.projects import ProjectService
from app.services.weather import WeatherService

logger = logging.getLogger(__name__)


class GardenService:
    """Service for managing the overall garden ecosystem"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_service = ProjectService(db)
        self.weather_service = WeatherService(db)
    
    async def get_complete_garden_state(
        self,
        season: Optional[str] = None,
        weather_type: Optional[str] = None,
        visitor_session: Optional[str] = None
    ) -> GardenState:
        """Get complete garden ecosystem state with personalization"""
        
        try:
            # Get all active projects
            query = select(Project).where(Project.status == 'active')
            if season:
                # Add season filtering logic if needed
                pass
            
            result = await self.db.execute(query.order_by(Project.planted_date))
            projects = result.scalars().all()
            
            # Convert to response models
            project_responses = []
            for p in projects:
                try:
                    project_responses.append(self._convert_project_to_response(p))
                except Exception as e:
                    logger.error(f"Error converting project {p.name}: {e}")
                    continue
            
            # Get skills constellations
            constellations = await self._get_skills_constellations()
            
            # Get current weather
            try:
                current_weather = await self.weather_service.get_current_weather()
            except Exception as e:
                logger.error(f"Error getting weather: {e}")
                # Create default weather response
                current_weather = self._create_default_weather_response()
            
            # Calculate garden metadata
            garden_age_days = await self._calculate_garden_age()
            total_growth_events = await self._count_total_growth_events()
            active_projects_count = len([p for p in projects if p.status == 'active'])
            
            # Get environmental conditions
            ambient_conditions = await self._calculate_ambient_conditions(current_weather)
            
            # Get personalized content if visitor session provided
            personalized_content = None
            if visitor_session:
                personalized_content = await self._get_personalized_content(visitor_session)
            
            return GardenState(
                success=True,
                message="Garden state retrieved successfully",
                projects=project_responses,
                skills_constellations=constellations,
                current_weather=current_weather,
                garden_age_days=garden_age_days,
                total_growth_events=total_growth_events,
                active_projects_count=active_projects_count,
                season=self._get_current_season(),
                time_of_day=self._get_time_of_day(),
                ambient_conditions=ambient_conditions,
                personalized_highlights=personalized_content.get('highlights') if personalized_content else None,
                recommended_projects=personalized_content.get('recommended_projects') if personalized_content else None,
                visitor_journey_suggestion=personalized_content.get('journey_suggestion') if personalized_content else None
            )
        except Exception as e:
            logger.error(f"Error in get_complete_garden_state: {e}")
            raise e
    
    async def get_garden_summary(self) -> GardenSummaryResponse:
        """Get condensed garden overview"""
        
        # Count projects by growth stage
        result = await self.db.execute(
            select(Project.growth_stage, func.count(Project.id))
            .where(Project.status == 'active')
            .group_by(Project.growth_stage)
        )
        stage_counts = {stage: count for stage, count in result.fetchall()}
        
        # Get total unique technologies
        result = await self.db.execute(
            select(func.array_length(Project.technologies, 1))
            .where(Project.technologies.isnot(None))
        )
        tech_arrays = result.scalars().all()
        unique_techs = set()
        for project_result in await self.db.execute(select(Project.technologies).where(Project.technologies.isnot(None))):
            if project_result[0]:
                unique_techs.update(project_result[0])
        
        # Get current weather summary
        current_weather = await self.weather_service.get_current_weather()
        weather_summary = {
            "type": current_weather.weather_type,
            "intensity": current_weather.intensity,
            "duration_hours": current_weather.duration_minutes / 60 if current_weather.duration_minutes else 0
        }
        
        # Get recent growth events
        result = await self.db.execute(
            select(ProjectGrowthLog, Project.name)
            .join(Project, ProjectGrowthLog.project_id == Project.id)
            .where(ProjectGrowthLog.new_stage.isnot(None))
            .order_by(desc(ProjectGrowthLog.recorded_at))
            .limit(5)
        )
        
        recent_growth_events = []
        for growth_log, project_name in result.fetchall():
            recent_growth_events.append({
                "project_name": project_name,
                "from_stage": growth_log.previous_stage,
                "to_stage": growth_log.new_stage,
                "timestamp": growth_log.recorded_at.isoformat()
            })
        
        # Get top skills
        result = await self.db.execute(
            select(Skill.name)
            .order_by(desc(Skill.proficiency_level), desc(Skill.projects_used_in))
            .limit(5)
        )
        top_skills = [skill_name for skill_name in result.scalars()]
        
        return GardenSummaryResponse(
            success=True,
            project_count_by_stage=stage_counts,
            total_technologies=len(unique_techs),
            weather_summary=weather_summary,
            recent_growth_events=recent_growth_events,
            top_skills=top_skills
        )
    
    async def plant_project_seed(
        self,
        seed_request: SeedPlantingRequest,
        visitor_session: str
    ) -> PlantedSeedResponse:
        """Plant a new project seed"""
        
        # Create the project at the specified position
        project_data = seed_request.project_data.dict()
        project_data.update({
            'position_x': seed_request.position.x,
            'position_y': seed_request.position.y, 
            'position_z': seed_request.position.z,
            'growth_stage': 'seed'
        })
        
        # Create project using project service
        project = await self.project_service.create_project(seed_request.project_data)
        
        # Create initial growth log entry
        growth_log = ProjectGrowthLog(
            project_id=project.id,
            new_stage='seed',
            growth_factor=seed_request.initial_growth_factor or 0.0,
            page_views=1,  # Planting counts as initial view
            interactions=1
        )
        self.db.add(growth_log)
        await self.db.commit()
        
        # Record visitor interaction
        await self._record_visitor_seed_planting(visitor_session, project.id)
        
        return PlantedSeedResponse(
            success=True,
            message="Seed planted successfully",
            project=self._convert_project_to_response(project),
            growth_triggered=True,
            estimated_growth_time=self._estimate_growth_time(project.plant_type)
        )
    
    async def get_garden_evolution(self) -> GardenEvolution:
        """Get garden evolution timeline and patterns"""
        
        # Get timeline events from growth logs and project creation
        timeline_events = []
        
        # Project plantings
        result = await self.db.execute(
            select(Project.name, Project.planted_date, Project.technologies, Project.plant_type)
            .order_by(Project.planted_date)
        )
        
        for project_name, planted_date, technologies, plant_type in result.fetchall():
            timeline_events.append({
                "type": "project_planted",
                "project_name": project_name,
                "timestamp": planted_date.isoformat(),
                "details": {
                    "initial_stage": "seed",
                    "technologies": technologies or [],
                    "plant_type": plant_type
                }
            })
        
        # Growth milestones
        result = await self.db.execute(
            select(ProjectGrowthLog, Project.name)
            .join(Project, ProjectGrowthLog.project_id == Project.id)
            .where(ProjectGrowthLog.new_stage.isnot(None))
            .order_by(ProjectGrowthLog.recorded_at)
        )
        
        for growth_log, project_name in result.fetchall():
            if growth_log.previous_stage and growth_log.new_stage:
                timeline_events.append({
                    "type": "growth_milestone",
                    "project_name": project_name,
                    "timestamp": growth_log.recorded_at.isoformat(),
                    "details": {
                        "stage_change": f"{growth_log.previous_stage}_to_{growth_log.new_stage}",
                        "trigger": "activity_threshold"
                    }
                })
        
        # Calculate growth velocity
        growth_velocity = await self._calculate_growth_velocity()
        
        # Analyze seasonal patterns
        seasonal_patterns = await self._analyze_seasonal_patterns()
        
        # Get milestone achievements
        milestone_achievements = await self._get_milestone_achievements()
        
        return GardenEvolution(
            timeline_events=sorted(timeline_events, key=lambda x: x["timestamp"]),
            growth_velocity=growth_velocity,
            seasonal_patterns=seasonal_patterns,
            milestone_achievements=milestone_achievements
        )
    
    async def get_interaction_suggestions(
        self,
        visitor_session: str
    ) -> List[GardenInteractionSuggestion]:
        """Get personalized interaction suggestions"""
        
        suggestions = []
        
        # Get visitor's session data
        result = await self.db.execute(
            select(VisitorSession)
            .where(VisitorSession.session_token == visitor_session)
        )
        session = result.scalar_one_or_none()
        
        # Suggest planting a seed if they haven't
        if not session or session.seeds_planted == 0:
            suggestions.append(GardenInteractionSuggestion(
                suggestion_type="plant_seed",
                title="Plant Your First Seed",
                description="Click on an empty spot to plant a new project idea",
                target_element={
                    "type": "garden_space",
                    "coordinates": {"x": 5.0, "y": 0.0, "z": 2.0}
                },
                expected_outcome="A new seed will appear and begin growing",
                difficulty="easy"
            ))
        
        # Suggest viewing project details
        if not session or len(session.projects_viewed or []) < 3:
            suggestions.append(GardenInteractionSuggestion(
                suggestion_type="explore_project",
                title="Explore a Growing Project",
                description="Click on a project to see its details and growth history",
                target_element={
                    "type": "project",
                    "growth_stage": "blooming"
                },
                expected_outcome="Detailed project information will be displayed",
                difficulty="easy"
            ))
        
        # Suggest skills constellation exploration
        suggestions.append(GardenInteractionSuggestion(
            suggestion_type="explore_constellation",
            title="Navigate the Skills Universe",
            description="Explore the constellation of skills and their connections",
            target_element={
                "type": "skills_constellation",
                "constellation": "Frontend Frameworks"
            },
            expected_outcome="Skills constellation will light up with connections",
            difficulty="medium"
        ))
        
        return suggestions
    
    async def calculate_garden_health(self) -> GardenHealth:
        """Calculate garden ecosystem health metrics"""
        
        # Get basic metrics
        result = await self.db.execute(
            select(func.count(Project.id))
            .where(Project.status == 'active')
        )
        total_projects = result.scalar() or 0
        
        # Calculate diversity score based on technologies and plant types
        diversity_score = await self._calculate_diversity_score()
        
        # Calculate growth momentum
        growth_momentum = await self._calculate_growth_momentum()
        
        # Calculate engagement vitality
        engagement_vitality = await self._calculate_engagement_vitality()
        
        # Overall health score (weighted average)
        overall_health_score = (
            diversity_score * 0.3 +
            growth_momentum * 0.4 +
            engagement_vitality * 0.3
        )
        
        # Generate recommendations
        recommendations = []
        at_risk_projects = []
        growth_opportunities = []
        
        if diversity_score < 0.6:
            recommendations.append("Consider adding projects with different technologies")
        
        if growth_momentum < 0.5:
            recommendations.append("Some projects need more development activity")
        
        # Identify projects that haven't been updated recently
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        result = await self.db.execute(
            select(Project.name)
            .where(
                and_(
                    Project.updated_at < cutoff_date,
                    Project.status == 'active'
                )
            )
        )
        at_risk_projects = [name for name in result.scalars()]
        
        # Identify growth opportunities
        if engagement_vitality > 0.8:
            growth_opportunities.append("High visitor engagement - perfect time for new projects")
        
        maintenance_status = "excellent" if overall_health_score > 0.8 else "good" if overall_health_score > 0.6 else "needs_attention"
        
        return GardenHealth(
            overall_health_score=overall_health_score,
            growth_momentum=growth_momentum,
            diversity_score=diversity_score,
            engagement_vitality=engagement_vitality,
            maintenance_status=maintenance_status,
            health_recommendations=recommendations,
            at_risk_projects=at_risk_projects,
            growth_opportunities=growth_opportunities
        )
    
    # Helper methods
    async def _get_skills_constellations(self) -> List[ConstellationResponse]:
        """Get organized skills constellations"""
        # This would be implemented to group skills by constellation
        # For now, return empty list
        return []
    
    async def _calculate_garden_age(self) -> int:
        """Calculate garden age in days"""
        result = await self.db.execute(
            select(func.min(Project.planted_date))
            .where(Project.status.in_(['active', 'archived']))
        )
        first_planted = result.scalar()
        
        if first_planted:
            delta = datetime.utcnow() - first_planted
            return delta.days
        return 0
    
    async def _count_total_growth_events(self) -> int:
        """Count total growth stage changes"""
        result = await self.db.execute(
            select(func.count(ProjectGrowthLog.id))
            .where(ProjectGrowthLog.new_stage.isnot(None))
        )
        return result.scalar() or 0
    
    async def _calculate_ambient_conditions(self, weather: WeatherStateResponse) -> Dict[str, Any]:
        """Calculate environmental conditions based on weather"""
        return {
            "light_intensity": 0.8 if weather.weather_type == "sunny" else 0.4,
            "wind_speed": 0.6 if weather.weather_type == "stormy" else 0.2,
            "humidity": 0.7 if weather.weather_type == "misty" else 0.4
        }
    
    def _get_current_season(self) -> str:
        """Determine current season"""
        month = datetime.utcnow().month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "autumn"
        else:
            return "winter"
    
    def _get_time_of_day(self) -> str:
        """Determine current time of day"""
        hour = datetime.utcnow().hour
        if 5 <= hour < 12:
            return "day"
        elif 12 <= hour < 17:
            return "day"
        elif 17 <= hour < 20:
            return "dusk"
        elif 20 <= hour < 5:
            return "night"
        else:
            return "dawn"
    
    async def _get_personalized_content(self, visitor_session: str) -> Dict[str, Any]:
        """Get personalized content for visitor"""
        # This would analyze visitor behavior and return personalized content
        return {
            "highlights": ["New growth in your favorite projects"],
            "recommended_projects": [],
            "journey_suggestion": "Start with the Featured Projects area"
        }
    
    def _estimate_growth_time(self, plant_type: str) -> int:
        """Estimate minutes until next growth stage"""
        growth_times = {
            "flower": 30,
            "herb": 45, 
            "shrub": 60,
            "vine": 90,
            "tree": 120
        }
        return growth_times.get(plant_type, 60)
    
    async def _record_visitor_seed_planting(self, visitor_session: str, project_id: UUID):
        """Record that visitor planted a seed"""
        result = await self.db.execute(
            select(VisitorSession)
            .where(VisitorSession.session_token == visitor_session)
        )
        session = result.scalar_one_or_none()
        
        if session:
            session.seeds_planted += 1
            await self.db.commit()
    
    async def _calculate_growth_velocity(self) -> float:
        """Calculate overall growth velocity"""
        # This would analyze growth patterns over time
        return 1.2  # Placeholder
    
    async def _analyze_seasonal_patterns(self) -> Dict[str, Any]:
        """Analyze seasonal growth patterns"""
        return {
            "spring": {"growth_rate": 1.4, "new_projects": 3},
            "summer": {"growth_rate": 1.1, "new_projects": 2}
        }
    
    async def _get_milestone_achievements(self) -> List[Dict[str, Any]]:
        """Get major milestone achievements"""
        return []
    
    async def _calculate_diversity_score(self) -> float:
        """Calculate technology and project diversity score"""
        # This would analyze the variety of technologies and project types
        return 0.75  # Placeholder
    
    async def _calculate_growth_momentum(self) -> float:
        """Calculate current growth momentum"""
        # This would analyze recent growth activity
        return 0.8  # Placeholder
    
    async def _calculate_engagement_vitality(self) -> float:
        """Calculate visitor engagement vitality"""
        # This would analyze visitor interaction patterns
        return 0.85  # Placeholder

    def _convert_project_to_response(self, project: Project) -> ProjectResponse:
        """Convert SQLAlchemy Project model to Pydantic ProjectResponse"""
        import json
        
        # Parse technologies from JSON string to list
        technologies = []
        if project.technologies:
            try:
                technologies = json.loads(project.technologies.replace("'", '"'))
            except:
                technologies = []
        
        return ProjectResponse(
            id=project.id,
            created_at=project.created_at,
            updated_at=project.updated_at,
            name=project.name,
            description=project.description,
            github_repo=project.github_repo,
            demo_url=project.demo_url,
            plant_type=project.plant_type,
            growth_stage=project.growth_stage,
            planted_date=project.planted_date,
            position_x=project.position_x,
            position_y=project.position_y,
            position_z=project.position_z,
            technologies=technologies,
            status=project.status,
            visibility=project.visibility,
            commit_count=project.commit_count,
            lines_of_code=project.lines_of_code,
            complexity_score=project.complexity_score,
            visitor_interactions=project.visitor_interactions
        )

    def _create_default_weather_response(self):
        """Create a default weather response when weather service fails"""
        from app.schemas.weather import WeatherStateResponse, WeatherType, TimeOfDay, Season
        from datetime import datetime
        from uuid import uuid4
        
        return WeatherStateResponse(
            id=str(uuid4()),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            weather_type=WeatherType.SUNNY,
            intensity=0.7,
            github_commits_today=0,
            coding_hours_today=0.0,
            music_mood=None,
            actual_weather=None,
            productivity_score=0.5,
            creativity_index=0.5,
            stress_level=0.3,
            time_of_day=TimeOfDay.DAY,
            season=Season.SUMMER,
            started_at=datetime.utcnow(),
            ended_at=None,
            is_active=True,
            duration_minutes=None
        )