"""
Project management service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_, update
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
from uuid import UUID

from app.models.projects import Project, ProjectGrowthLog
from app.models.visitors import VisitorSession
from app.schemas.base import PaginationParams
from app.schemas.projects import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse,
    InteractionEvent, InteractionResponse, ProjectGrowthLogResponse
)

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for project management and growth calculations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_projects(
        self,
        filters: Dict[str, Any] = None,
        pagination: PaginationParams = None
    ) -> Tuple[List[Project], int]:
        """List projects with filtering and pagination"""
        
        query = select(Project)
        count_query = select(func.count(Project.id))
        
        # Apply filters
        if filters:
            filter_conditions = []
            
            if filters.get('status'):
                filter_conditions.append(Project.status == filters['status'])
            
            if filters.get('growth_stage'):
                filter_conditions.append(Project.growth_stage == filters['growth_stage'])
            
            if filters.get('plant_type'):
                filter_conditions.append(Project.plant_type == filters['plant_type'])
            
            if filters.get('technology'):
                filter_conditions.append(Project.technologies.contains([filters['technology']]))
            
            if filter_conditions:
                query = query.where(and_(*filter_conditions))
                count_query = count_query.where(and_(*filter_conditions))
        
        # Get total count
        result = await self.db.execute(count_query)
        total_count = result.scalar()
        
        # Apply pagination
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.page_size)
        
        # Execute query
        result = await self.db.execute(query.order_by(desc(Project.updated_at)))
        projects = result.scalars().all()
        
        return projects, total_count
    
    async def create_project(self, project_data: ProjectCreate) -> Project:
        """Create a new project"""
        
        project = Project(
            **project_data.dict(),
            growth_stage='seed',
            planted_date=datetime.utcnow()
        )
        
        self.db.add(project)
        await self.db.flush()  # Get the ID without committing
        
        # Create initial growth log
        initial_growth_log = ProjectGrowthLog(
            project_id=project.id,
            new_stage='seed',
            growth_factor=0.0,
            recorded_at=datetime.utcnow()
        )
        
        self.db.add(initial_growth_log)
        await self.db.commit()
        await self.db.refresh(project)
        
        logger.info(f"Project created: {project.name} ({project.id})")
        return project
    
    async def get_project_details(
        self,
        project_id: UUID,
        visitor_session: Optional[str] = None
    ) -> Optional[ProjectDetailResponse]:
        """Get detailed project information"""
        
        # Get project
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return None
        
        # Get growth logs
        result = await self.db.execute(
            select(ProjectGrowthLog)
            .where(ProjectGrowthLog.project_id == project_id)
            .order_by(desc(ProjectGrowthLog.recorded_at))
            .limit(10)
        )
        growth_logs = result.scalars().all()
        
        # Build engagement metrics
        engagement_metrics = await self._calculate_engagement_metrics(project_id)
        
        # Get recent activity (placeholder - would integrate with GitHub API)
        recent_activity = await self._get_recent_activity(project)
        
        # Get related skills (based on technologies)
        related_skills = project.technologies or []
        
        # Record view if visitor session provided
        if visitor_session:
            await self._record_project_view(project_id, visitor_session)
        
        return ProjectDetailResponse(
            **ProjectResponse.model_validate(project).dict(),
            growth_logs=[ProjectGrowthLogResponse.model_validate(log) for log in growth_logs],
            related_skills=related_skills,
            engagement_metrics=engagement_metrics,
            recent_activity=recent_activity
        )
    
    async def update_project(
        self,
        project_id: UUID,
        project_data: ProjectUpdate
    ) -> Optional[Project]:
        """Update project information"""
        
        # Get existing project
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return None
        
        # Update fields
        update_data = project_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        project.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(project)
        
        logger.info(f"Project updated: {project.name} ({project.id})")
        return project
    
    async def delete_project(self, project_id: UUID) -> bool:
        """Delete a project"""
        
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return False
        
        await self.db.delete(project)
        await self.db.commit()
        
        logger.info(f"Project deleted: {project_id}")
        return True
    
    async def record_interaction(
        self,
        project_id: UUID,
        interaction: InteractionEvent,
        visitor_session: str
    ) -> InteractionResponse:
        """Record visitor interaction with project"""
        
        # Get project
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise ValueError("Project not found")
        
        # Update project interaction count
        project.visitor_interactions += 1
        
        # Update visitor session
        await self._update_visitor_session_interaction(
            visitor_session, project_id, interaction
        )
        
        # Check if interaction should trigger growth
        growth_triggered = await self._check_growth_trigger(project, interaction)
        new_growth_stage = None
        
        if growth_triggered:
            new_growth_stage = await self._calculate_next_growth_stage(project)
            if new_growth_stage and new_growth_stage != project.growth_stage:
                old_stage = project.growth_stage
                project.growth_stage = new_growth_stage
                
                # Create growth log
                growth_log = ProjectGrowthLog(
                    project_id=project.id,
                    previous_stage=old_stage,
                    new_stage=new_growth_stage,
                    interactions=1,
                    growth_factor=self._calculate_growth_factor(project),
                    recorded_at=datetime.utcnow()
                )
                self.db.add(growth_log)
        
        await self.db.commit()
        
        return InteractionResponse(
            success=True,
            message="Interaction recorded successfully",
            interaction_recorded=True,
            growth_triggered=growth_triggered,
            new_growth_stage=new_growth_stage,
            engagement_score_delta=0.1 if growth_triggered else 0.05
        )
    
    async def trigger_growth_calculation(self, project_id: UUID):
        """Trigger growth calculation for a project"""
        
        # Get project
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return
        
        # Calculate new growth metrics
        growth_metrics = await self._calculate_comprehensive_growth_metrics(project)
        
        # Determine if growth stage should change
        new_stage = await self._determine_growth_stage_from_metrics(
            project, growth_metrics
        )
        
        if new_stage != project.growth_stage:
            old_stage = project.growth_stage
            project.growth_stage = new_stage
            
            # Create comprehensive growth log
            growth_log = ProjectGrowthLog(
                project_id=project.id,
                previous_stage=old_stage,
                new_stage=new_stage,
                commits_delta=growth_metrics.get('commits_delta', 0),
                lines_added=growth_metrics.get('lines_added', 0),
                lines_removed=growth_metrics.get('lines_removed', 0),
                complexity_change=growth_metrics.get('complexity_change', 0),
                github_activity=growth_metrics.get('github_activity'),
                page_views=growth_metrics.get('page_views', 0),
                interactions=growth_metrics.get('interactions', 0),
                growth_factor=growth_metrics.get('growth_factor', 0),
                recorded_at=datetime.utcnow()
            )
            
            self.db.add(growth_log)
            await self.db.commit()
            
            logger.info(f"Growth stage changed: {project.name} from {old_stage} to {new_stage}")
    
    async def get_project_analytics(self, project_id: UUID) -> Optional[Dict[str, Any]]:
        """Get analytics data for a project"""
        
        # Verify project exists
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return None
        
        # Get growth history count
        result = await self.db.execute(
            select(func.count(ProjectGrowthLog.id))
            .where(ProjectGrowthLog.project_id == project_id)
        )
        total_growth_events = result.scalar() or 0
        
        # Get visitor analytics
        result = await self.db.execute(
            select(
                func.count(VisitorSession.id),
                func.avg(
                    func.cast(
                        func.jsonb_extract_path_text(
                            VisitorSession.time_spent_per_project,
                            str(project_id)
                        ),
                        "integer"
                    )
                )
            )
            .where(VisitorSession.projects_viewed.contains([project_id]))
        )
        
        visitor_result = result.fetchone()
        unique_visitors = visitor_result[0] or 0
        avg_view_time = visitor_result[1] or 0
        
        # Calculate other metrics
        days_since_last_growth = await self._calculate_days_since_last_growth(project_id)
        interaction_rate = await self._calculate_interaction_rate(project_id)
        
        return {
            "project_id": str(project_id),
            "project_name": project.name,
            "current_stage": project.growth_stage,
            "total_growth_events": total_growth_events,
            "growth_velocity": await self._calculate_growth_velocity(project_id),
            "days_since_last_growth": days_since_last_growth,
            "total_views": unique_visitors,
            "unique_visitors": unique_visitors,
            "average_view_duration": avg_view_time,
            "interaction_rate": interaction_rate,
            "commit_frequency": await self._calculate_commit_frequency(project),
            "code_complexity_trend": "stable",  # Placeholder
            "technology_diversity": len(project.technologies) if project.technologies else 0,
            "demo_click_rate": 0.15,  # Placeholder
            "github_click_rate": 0.08,  # Placeholder
            "social_shares": 0  # Placeholder
        }
    
    async def update_interaction_analytics(
        self,
        project_id: UUID,
        interaction_type: str
    ):
        """Update analytics based on interaction"""
        
        # This would update various analytics metrics
        # For now, just log the interaction
        logger.debug(f"Analytics updated for project {project_id}: {interaction_type}")
    
    # Helper methods
    async def _calculate_engagement_metrics(self, project_id: UUID) -> Dict[str, Any]:
        """Calculate engagement metrics for a project"""
        
        # Get recent visitor sessions that viewed this project
        result = await self.db.execute(
            select(
                func.count(VisitorSession.id),
                func.avg(VisitorSession.engagement_score)
            )
            .where(VisitorSession.projects_viewed.contains([project_id]))
        )
        
        visitor_result = result.fetchone()
        total_visitors = visitor_result[0] or 0
        avg_engagement = visitor_result[1] or 0
        
        return {
            "total_visitors": total_visitors,
            "average_engagement_score": avg_engagement,
            "recent_interactions": await self._count_recent_interactions(project_id)
        }
    
    async def _get_recent_activity(self, project: Project) -> Dict[str, Any]:
        """Get recent activity for a project (placeholder for GitHub integration)"""
        
        return {
            "recent_commits": [],
            "recent_deployments": [],
            "last_update": project.updated_at.isoformat() if project.updated_at else None
        }
    
    async def _record_project_view(self, project_id: UUID, visitor_session: str):
        """Record that a visitor viewed a project"""
        
        result = await self.db.execute(
            select(VisitorSession)
            .where(VisitorSession.session_token == visitor_session)
        )
        session = result.scalar_one_or_none()
        
        if session:
            # Add project to viewed list if not already there
            viewed_projects = session.projects_viewed or []
            if project_id not in viewed_projects:
                viewed_projects.append(project_id)
                session.projects_viewed = viewed_projects
                await self.db.commit()
    
    async def _update_visitor_session_interaction(
        self,
        visitor_session: str,
        project_id: UUID,
        interaction: InteractionEvent
    ):
        """Update visitor session with interaction data"""
        
        result = await self.db.execute(
            select(VisitorSession)
            .where(VisitorSession.session_token == visitor_session)
        )
        session = result.scalar_one_or_none()
        
        if session:
            # Update interaction count
            session.clicks_count += 1
            
            # Update interaction events
            interaction_events = session.interaction_events or []
            interaction_events.append({
                "project_id": str(project_id),
                "type": interaction.interaction_type,
                "timestamp": interaction.timestamp.isoformat(),
                "duration": interaction.duration_seconds,
                "metadata": interaction.metadata
            })
            session.interaction_events = interaction_events
            
            # Update time spent on project
            time_spent = session.time_spent_per_project or {}
            project_key = str(project_id)
            time_spent[project_key] = time_spent.get(project_key, 0) + (interaction.duration_seconds or 10)
            session.time_spent_per_project = time_spent
            
            session.last_activity_at = datetime.utcnow()
    
    async def _check_growth_trigger(
        self,
        project: Project,
        interaction: InteractionEvent
    ) -> bool:
        """Check if interaction should trigger growth"""
        
        # Simple growth trigger logic
        high_value_interactions = ['demo_launch', 'github_visit', 'seed_plant']
        
        if interaction.interaction_type in high_value_interactions:
            return True
        
        # Check if enough interactions have accumulated
        if project.visitor_interactions > 0 and project.visitor_interactions % 10 == 0:
            return True
        
        return False
    
    async def _calculate_next_growth_stage(self, project: Project) -> Optional[str]:
        """Calculate the next growth stage for a project"""
        
        stage_progression = ['seed', 'sprout', 'growing', 'blooming', 'mature']
        
        try:
            current_index = stage_progression.index(project.growth_stage)
            if current_index < len(stage_progression) - 1:
                return stage_progression[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def _calculate_growth_factor(self, project: Project) -> float:
        """Calculate growth factor based on project metrics"""
        
        # Simple growth factor calculation
        base_factor = 0.1
        
        # Add factors for various metrics
        if project.visitor_interactions > 5:
            base_factor += 0.2
        
        if project.commit_count > 10:
            base_factor += 0.3
        
        if project.lines_of_code > 1000:
            base_factor += 0.2
        
        return min(base_factor, 1.0)
    
    async def _calculate_comprehensive_growth_metrics(
        self,
        project: Project
    ) -> Dict[str, Any]:
        """Calculate comprehensive growth metrics (placeholder for GitHub integration)"""
        
        return {
            "commits_delta": 0,
            "lines_added": 0,
            "lines_removed": 0,
            "complexity_change": 0,
            "github_activity": {},
            "page_views": project.visitor_interactions,
            "interactions": project.visitor_interactions,
            "growth_factor": self._calculate_growth_factor(project)
        }
    
    async def _determine_growth_stage_from_metrics(
        self,
        project: Project,
        metrics: Dict[str, Any]
    ) -> str:
        """Determine growth stage based on comprehensive metrics"""
        
        growth_factor = metrics.get('growth_factor', 0)
        interactions = metrics.get('interactions', 0)
        
        if growth_factor >= 0.8 or interactions >= 50:
            return 'mature'
        elif growth_factor >= 0.6 or interactions >= 25:
            return 'blooming'
        elif growth_factor >= 0.4 or interactions >= 10:
            return 'growing'
        elif growth_factor >= 0.2 or interactions >= 5:
            return 'sprout'
        else:
            return 'seed'
    
    async def _calculate_days_since_last_growth(self, project_id: UUID) -> int:
        """Calculate days since last growth event"""
        
        result = await self.db.execute(
            select(func.max(ProjectGrowthLog.recorded_at))
            .where(ProjectGrowthLog.project_id == project_id)
        )
        last_growth = result.scalar()
        
        if last_growth:
            delta = datetime.utcnow() - last_growth
            return delta.days
        
        return 0
    
    async def _calculate_interaction_rate(self, project_id: UUID) -> float:
        """Calculate visitor interaction rate for project"""
        
        # Get total visitors and interactions
        result = await self.db.execute(
            select(
                func.count(VisitorSession.id),
                func.sum(
                    func.jsonb_array_length(
                        VisitorSession.interaction_events
                    )
                )
            )
            .where(VisitorSession.projects_viewed.contains([project_id]))
        )
        
        visitor_result = result.fetchone()
        total_visitors = visitor_result[0] or 0
        total_interactions = visitor_result[1] or 0
        
        if total_visitors > 0:
            return total_interactions / total_visitors
        return 0.0
    
    async def _calculate_growth_velocity(self, project_id: UUID) -> float:
        """Calculate growth velocity over time"""
        
        # Get growth events in last 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        result = await self.db.execute(
            select(func.count(ProjectGrowthLog.id))
            .where(
                and_(
                    ProjectGrowthLog.project_id == project_id,
                    ProjectGrowthLog.recorded_at >= cutoff_date
                )
            )
        )
        recent_growth_events = result.scalar() or 0
        
        # Return growth events per week
        return recent_growth_events / 4.0
    
    async def _calculate_commit_frequency(self, project: Project) -> float:
        """Calculate commit frequency (placeholder for GitHub integration)"""
        
        # This would integrate with GitHub API to get actual commit frequency
        return project.commit_count / 10.0  # Placeholder calculation
    
    async def _count_recent_interactions(self, project_id: UUID) -> int:
        """Count recent interactions for a project"""
        
        cutoff_date = datetime.utcnow() - timedelta(hours=24)
        result = await self.db.execute(
            select(func.count(VisitorSession.id))
            .where(
                and_(
                    VisitorSession.projects_viewed.contains([project_id]),
                    VisitorSession.last_activity_at >= cutoff_date
                )
            )
        )
        
        return result.scalar() or 0