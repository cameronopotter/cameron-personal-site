"""
Growth algorithm engine for calculating project growth stages and evolution.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .github_service import GitHubService, GitHubActivity, GitHubRepository
from .wakatime_service import WakaTimeService, ProductivityAnalysis
from .websocket_manager import websocket_manager, WebSocketEvent, EventType

import logging
logger = logging.getLogger(__name__)


class GrowthStage(str, Enum):
    """Project growth stages"""
    SEED = "seed"              # Initial concept, minimal code
    SEEDLING = "seedling"      # Basic structure, first commits
    SAPLING = "sapling"        # Growing structure, regular commits
    YOUNG_TREE = "young_tree"  # Established patterns, consistent development
    MATURE_TREE = "mature_tree" # Well-developed, stable project
    ANCIENT_TREE = "ancient_tree" # Highly mature, significant impact


class GrowthFactor(str, Enum):
    """Factors that influence growth"""
    COMMIT_FREQUENCY = "commit_frequency"
    CODE_COMPLEXITY = "code_complexity"
    TIME_INVESTED = "time_invested"
    EXTERNAL_ENGAGEMENT = "external_engagement"
    PROJECT_AGE = "project_age"
    CONSISTENCY = "consistency"
    INNOVATION = "innovation"


@dataclass
class GrowthMetrics:
    """Comprehensive growth metrics for a project"""
    project_name: str
    current_stage: GrowthStage
    growth_score: float  # 0.0 to 1.0
    velocity: float      # Growth units per day
    momentum: float      # Rate of acceleration
    
    # Individual factor scores
    commit_score: float
    complexity_score: float
    time_score: float
    engagement_score: float
    age_score: float
    consistency_score: float
    innovation_score: float
    
    # Predictions
    next_stage_eta: Optional[int]  # Days to next stage
    projected_growth: float       # Expected growth in 30 days
    
    # Metadata
    last_updated: datetime
    confidence: float  # 0.0 to 1.0


@dataclass
class GrowthEvent:
    """Growth milestone events"""
    project_name: str
    event_type: str  # "stage_change", "milestone", "acceleration"
    description: str
    old_value: Optional[float]
    new_value: float
    timestamp: datetime
    significance: float  # 0.0 to 1.0


class GrowthEngine:
    """Project growth calculation and analysis engine"""
    
    def __init__(self):
        self.github_service = GitHubService()
        self.wakatime_service = WakaTimeService()
        
        # Growth stage thresholds (cumulative scores)
        self.stage_thresholds = {
            GrowthStage.SEED: 0.1,
            GrowthStage.SEEDLING: 0.25,
            GrowthStage.SAPLING: 0.45,
            GrowthStage.YOUNG_TREE: 0.65,
            GrowthStage.MATURE_TREE: 0.80,
            GrowthStage.ANCIENT_TREE: 0.95
        }
        
        # Factor weights for overall growth score
        self.factor_weights = {
            GrowthFactor.COMMIT_FREQUENCY: 0.20,
            GrowthFactor.CODE_COMPLEXITY: 0.15,
            GrowthFactor.TIME_INVESTED: 0.20,
            GrowthFactor.EXTERNAL_ENGAGEMENT: 0.15,
            GrowthFactor.PROJECT_AGE: 0.10,
            GrowthFactor.CONSISTENCY: 0.15,
            GrowthFactor.INNOVATION: 0.05
        }
        
        # Cache for previous calculations
        self._growth_cache: Dict[str, GrowthMetrics] = {}
        self._last_calculations: Dict[str, datetime] = {}
    
    async def calculate_project_growth(
        self, 
        project_name: str, 
        force_refresh: bool = False
    ) -> Optional[GrowthMetrics]:
        """Calculate comprehensive growth metrics for a project"""
        
        # Check cache (refresh every 30 minutes)
        if not force_refresh and project_name in self._growth_cache:
            last_calc = self._last_calculations.get(project_name)
            if last_calc and (datetime.utcnow() - last_calc).seconds < 1800:
                return self._growth_cache[project_name]
        
        try:
            # Gather data from multiple sources
            github_data = await self._get_github_metrics(project_name)
            wakatime_data = await self._get_wakatime_metrics(project_name)
            
            if not github_data:
                logger.warning(f"No GitHub data available for project: {project_name}")
                return None
            
            # Calculate individual factor scores
            commit_score = self._calculate_commit_score(github_data)
            complexity_score = self._calculate_complexity_score(github_data)
            time_score = self._calculate_time_score(wakatime_data) if wakatime_data else 0.5
            engagement_score = self._calculate_engagement_score(github_data)
            age_score = self._calculate_age_score(github_data)
            consistency_score = self._calculate_consistency_score(github_data)
            innovation_score = self._calculate_innovation_score(github_data)
            
            # Calculate weighted overall growth score
            factor_scores = {
                GrowthFactor.COMMIT_FREQUENCY: commit_score,
                GrowthFactor.CODE_COMPLEXITY: complexity_score,
                GrowthFactor.TIME_INVESTED: time_score,
                GrowthFactor.EXTERNAL_ENGAGEMENT: engagement_score,
                GrowthFactor.PROJECT_AGE: age_score,
                GrowthFactor.CONSISTENCY: consistency_score,
                GrowthFactor.INNOVATION: innovation_score
            }
            
            growth_score = sum(
                score * self.factor_weights[factor]
                for factor, score in factor_scores.items()
            )
            
            # Determine growth stage
            current_stage = self._determine_growth_stage(growth_score)
            
            # Calculate velocity and momentum
            velocity, momentum = self._calculate_velocity_momentum(project_name, growth_score)
            
            # Make predictions
            next_stage_eta, projected_growth = self._make_growth_predictions(
                growth_score, velocity, momentum, current_stage
            )
            
            # Calculate confidence based on data quality
            confidence = self._calculate_confidence(github_data, wakatime_data)
            
            # Create growth metrics
            metrics = GrowthMetrics(
                project_name=project_name,
                current_stage=current_stage,
                growth_score=growth_score,
                velocity=velocity,
                momentum=momentum,
                commit_score=commit_score,
                complexity_score=complexity_score,
                time_score=time_score,
                engagement_score=engagement_score,
                age_score=age_score,
                consistency_score=consistency_score,
                innovation_score=innovation_score,
                next_stage_eta=next_stage_eta,
                projected_growth=projected_growth,
                last_updated=datetime.utcnow(),
                confidence=confidence
            )
            
            # Check for significant changes
            await self._check_growth_events(project_name, metrics)
            
            # Update cache
            self._growth_cache[project_name] = metrics
            self._last_calculations[project_name] = datetime.utcnow()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate growth for {project_name}: {e}")
            return None
    
    async def _get_github_metrics(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get GitHub metrics for a project"""
        try:
            # Get repository info
            repos_response = await self.github_service.get_user_repositories()
            if not repos_response.success:
                return None
            
            repo = next((r for r in repos_response.data if r.name == project_name), None)
            if not repo:
                return None
            
            # Get commit data
            month_ago = datetime.utcnow() - timedelta(days=30)
            commits_response = await self.github_service.get_repository_commits(
                project_name, since=month_ago, limit=100
            )
            
            # Get languages
            languages_response = await self.github_service.get_repository_languages(project_name)
            
            return {
                "repository": repo,
                "commits": commits_response.data if commits_response.success else [],
                "languages": languages_response.data if languages_response.success else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get GitHub metrics for {project_name}: {e}")
            return None
    
    async def _get_wakatime_metrics(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get WakaTime metrics for a project"""
        try:
            if not self.wakatime_service.is_available():
                return None
            
            # Get project-specific time tracking data
            project_data = await self.wakatime_service.get_project_growth_data(project_name, 30)
            
            # Get overall productivity analysis
            productivity_response = await self.wakatime_service.get_productivity_analysis(30)
            productivity = productivity_response.data if productivity_response.success else None
            
            return {
                "project_data": project_data,
                "productivity": productivity
            }
            
        except Exception as e:
            logger.error(f"Failed to get WakaTime metrics for {project_name}: {e}")
            return None
    
    def _calculate_commit_score(self, github_data: Dict[str, Any]) -> float:
        """Calculate score based on commit frequency and patterns"""
        commits = github_data.get("commits", [])
        
        if not commits:
            return 0.1  # Minimal score for no recent commits
        
        # Analyze commit frequency
        commit_count = len(commits)
        days_with_commits = len(set(c.committed_at.date() for c in commits))
        
        # Score based on frequency (max 30 commits in 30 days = 1.0)
        frequency_score = min(commit_count / 30, 1.0)
        
        # Consistency bonus (commits spread across days)
        consistency_bonus = min(days_with_commits / 20, 0.3)  # Up to 30% bonus
        
        # Recent activity bonus
        recent_commits = [c for c in commits if c.committed_at >= datetime.utcnow() - timedelta(days=7)]
        recent_bonus = min(len(recent_commits) / 10, 0.2)  # Up to 20% bonus
        
        return min(frequency_score + consistency_bonus + recent_bonus, 1.0)
    
    def _calculate_complexity_score(self, github_data: Dict[str, Any]) -> float:
        """Calculate score based on code complexity indicators"""
        repo = github_data.get("repository")
        commits = github_data.get("commits", [])
        languages_data = github_data.get("languages")
        
        if not repo:
            return 0.1
        
        # Repository size score (logarithmic)
        size_score = min(math.log(max(repo.size, 1)) / math.log(10000), 1.0)  # Up to 10MB
        
        # Language diversity score
        language_count = len(languages_data.languages) if languages_data else 1
        language_score = min(language_count / 5, 0.3)  # Up to 30% for 5+ languages
        
        # Commit complexity (lines changed)
        if commits:
            avg_changes = sum(c.additions + c.deletions for c in commits) / len(commits)
            complexity_score = min(avg_changes / 100, 0.4)  # Up to 40% for 100+ lines/commit
        else:
            complexity_score = 0.0
        
        return min(size_score + language_score + complexity_score, 1.0)
    
    def _calculate_time_score(self, wakatime_data: Dict[str, Any]) -> float:
        """Calculate score based on time invested"""
        if not wakatime_data or "project_data" not in wakatime_data:
            return 0.5  # Default score when no time tracking
        
        project_data = wakatime_data["project_data"]
        
        if "error" in project_data:
            return 0.5
        
        # Total time score (logarithmic, max at 100 hours)
        total_hours = project_data.get("total_time_hours", 0)
        time_score = min(math.log(max(total_hours, 1)) / math.log(100), 0.7)
        
        # Weekly consistency score
        weekly_hours = project_data.get("avg_weekly_hours", 0)
        consistency_score = min(weekly_hours / 10, 0.3)  # Up to 30% for 10+ hours/week
        
        return min(time_score + consistency_score, 1.0)
    
    def _calculate_engagement_score(self, github_data: Dict[str, Any]) -> float:
        """Calculate score based on external engagement"""
        repo = github_data.get("repository")
        
        if not repo:
            return 0.1
        
        # Stars score (logarithmic)
        stars_score = min(math.log(max(repo.stars, 1)) / math.log(100), 0.5)  # Up to 50% for 100+ stars
        
        # Forks score (logarithmic)
        forks_score = min(math.log(max(repo.forks, 1)) / math.log(20), 0.3)  # Up to 30% for 20+ forks
        
        # Activity score (recent pushes)
        days_since_push = (datetime.utcnow() - repo.pushed_at).days
        activity_score = max(0, 0.2 - (days_since_push / 100))  # Up to 20%, decreases over time
        
        return min(stars_score + forks_score + activity_score, 1.0)
    
    def _calculate_age_score(self, github_data: Dict[str, Any]) -> float:
        """Calculate score based on project age (maturity factor)"""
        repo = github_data.get("repository")
        
        if not repo:
            return 0.1
        
        # Age in days
        age_days = (datetime.utcnow() - repo.created_at).days
        
        # Maturity curve: starts low, peaks around 1 year, then stabilizes
        if age_days < 30:
            return age_days / 30 * 0.3  # 0-30%
        elif age_days < 365:
            return 0.3 + ((age_days - 30) / 335) * 0.5  # 30-80%
        else:
            return min(0.8 + ((age_days - 365) / 1095) * 0.2, 1.0)  # 80-100% over 3 years
    
    def _calculate_consistency_score(self, github_data: Dict[str, Any]) -> float:
        """Calculate score based on development consistency"""
        commits = github_data.get("commits", [])
        
        if len(commits) < 5:
            return 0.2  # Low score for few commits
        
        # Analyze commit timing patterns
        commit_dates = [c.committed_at.date() for c in commits]
        unique_dates = set(commit_dates)
        
        # Day spread score
        total_span = (max(commit_dates) - min(commit_dates)).days if len(unique_dates) > 1 else 1
        day_coverage = len(unique_dates) / max(total_span, 1)
        spread_score = min(day_coverage * 2, 0.5)  # Up to 50%
        
        # Regular intervals score
        intervals = []
        sorted_dates = sorted(unique_dates)
        for i in range(1, len(sorted_dates)):
            intervals.append((sorted_dates[i] - sorted_dates[i-1]).days)
        
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            interval_variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)
            regularity_score = max(0, 0.5 - (interval_variance / 100))  # Up to 50%
        else:
            regularity_score = 0.0
        
        return min(spread_score + regularity_score, 1.0)
    
    def _calculate_innovation_score(self, github_data: Dict[str, Any]) -> float:
        """Calculate score based on innovation indicators"""
        repo = github_data.get("repository")
        commits = github_data.get("commits", [])
        
        if not repo:
            return 0.1
        
        innovation_signals = 0
        
        # Topic diversity (GitHub topics)
        if repo.topics:
            innovation_signals += min(len(repo.topics) / 10, 0.3)
        
        # Modern language usage
        if repo.language:
            modern_languages = ["Rust", "Go", "TypeScript", "Kotlin", "Swift", "Dart"]
            if repo.language in modern_languages:
                innovation_signals += 0.2
        
        # Frequent experimentation (many small commits)
        if commits:
            small_commits = [c for c in commits if c.additions + c.deletions < 50]
            experiment_ratio = len(small_commits) / len(commits)
            if experiment_ratio > 0.3:  # 30%+ small commits suggests experimentation
                innovation_signals += 0.3
        
        # Recent activity on cutting-edge topics
        cutting_edge_keywords = ["ai", "ml", "blockchain", "webassembly", "quantum", "edge"]
        description = (repo.description or "").lower()
        for keyword in cutting_edge_keywords:
            if keyword in description:
                innovation_signals += 0.1
                break
        
        return min(innovation_signals, 1.0)
    
    def _determine_growth_stage(self, growth_score: float) -> GrowthStage:
        """Determine growth stage based on overall score"""
        for stage, threshold in reversed(list(self.stage_thresholds.items())):
            if growth_score >= threshold:
                return stage
        return GrowthStage.SEED
    
    def _calculate_velocity_momentum(
        self, 
        project_name: str, 
        current_score: float
    ) -> Tuple[float, float]:
        """Calculate growth velocity and momentum"""
        # Get previous score for velocity calculation
        previous_metrics = self._growth_cache.get(project_name)
        
        if previous_metrics:
            time_diff = (datetime.utcnow() - previous_metrics.last_updated).total_seconds() / 86400  # days
            velocity = (current_score - previous_metrics.growth_score) / max(time_diff, 1)
            
            # Momentum = change in velocity
            momentum = velocity - previous_metrics.velocity
        else:
            # Estimate velocity from current activity
            velocity = current_score * 0.1  # Rough estimate
            momentum = 0.0
        
        return velocity, momentum
    
    def _make_growth_predictions(
        self, 
        current_score: float, 
        velocity: float, 
        momentum: float, 
        current_stage: GrowthStage
    ) -> Tuple[Optional[int], float]:
        """Make growth predictions"""
        
        # Find next stage threshold
        next_stage_threshold = None
        for stage, threshold in self.stage_thresholds.items():
            if threshold > current_score:
                next_stage_threshold = threshold
                break
        
        # Calculate ETA to next stage
        next_stage_eta = None
        if next_stage_threshold and velocity > 0:
            days_to_next = (next_stage_threshold - current_score) / velocity
            if days_to_next > 0:
                next_stage_eta = int(days_to_next)
        
        # Project growth in 30 days (with momentum)
        projected_velocity = velocity + (momentum * 30)  # Velocity after 30 days
        avg_velocity = (velocity + projected_velocity) / 2  # Average velocity
        projected_growth = current_score + (avg_velocity * 30)
        projected_growth = min(max(projected_growth, 0), 1.0)
        
        return next_stage_eta, projected_growth
    
    def _calculate_confidence(
        self, 
        github_data: Optional[Dict[str, Any]], 
        wakatime_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate confidence level based on data availability and quality"""
        confidence = 0.0
        
        # GitHub data quality
        if github_data:
            confidence += 0.5  # Base for having GitHub data
            
            commits = github_data.get("commits", [])
            if len(commits) >= 10:
                confidence += 0.2  # Good commit history
            
            if github_data.get("languages"):
                confidence += 0.1  # Language data available
        
        # WakaTime data quality
        if wakatime_data and "project_data" in wakatime_data:
            project_data = wakatime_data["project_data"]
            if "error" not in project_data:
                confidence += 0.2  # Time tracking data available
        
        return min(confidence, 1.0)
    
    async def _check_growth_events(self, project_name: str, new_metrics: GrowthMetrics):
        """Check for significant growth events and broadcast them"""
        previous_metrics = self._growth_cache.get(project_name)
        
        if not previous_metrics:
            return  # No previous data to compare
        
        events = []
        
        # Check for stage changes
        if new_metrics.current_stage != previous_metrics.current_stage:
            events.append(GrowthEvent(
                project_name=project_name,
                event_type="stage_change",
                description=f"Project evolved from {previous_metrics.current_stage.value} to {new_metrics.current_stage.value}",
                old_value=None,
                new_value=new_metrics.growth_score,
                timestamp=datetime.utcnow(),
                significance=0.9
            ))
        
        # Check for significant score changes
        score_change = new_metrics.growth_score - previous_metrics.growth_score
        if abs(score_change) > 0.05:  # 5% change threshold
            events.append(GrowthEvent(
                project_name=project_name,
                event_type="milestone" if score_change > 0 else "regression",
                description=f"Growth score {'increased' if score_change > 0 else 'decreased'} by {abs(score_change):.2%}",
                old_value=previous_metrics.growth_score,
                new_value=new_metrics.growth_score,
                timestamp=datetime.utcnow(),
                significance=min(abs(score_change) * 2, 1.0)
            ))
        
        # Check for velocity changes (acceleration/deceleration)
        velocity_change = new_metrics.velocity - previous_metrics.velocity
        if abs(velocity_change) > 0.01:  # Significant velocity change
            events.append(GrowthEvent(
                project_name=project_name,
                event_type="acceleration" if velocity_change > 0 else "deceleration",
                description=f"Growth velocity {'accelerated' if velocity_change > 0 else 'decelerated'}",
                old_value=previous_metrics.velocity,
                new_value=new_metrics.velocity,
                timestamp=datetime.utcnow(),
                significance=min(abs(velocity_change) * 10, 1.0)
            ))
        
        # Broadcast significant events
        for event in events:
            if event.significance > 0.5:  # Only broadcast significant events
                await websocket_manager.broadcast_event(WebSocketEvent(
                    type=EventType.GROWTH_STAGE_CHANGED,
                    data={
                        "project": event.project_name,
                        "event_type": event.event_type,
                        "description": event.description,
                        "significance": event.significance,
                        "new_stage": new_metrics.current_stage.value,
                        "growth_score": new_metrics.growth_score
                    },
                    timestamp=event.timestamp,
                    source="growth_engine"
                ))
    
    async def get_portfolio_overview(self) -> Dict[str, Any]:
        """Get overview of all projects in portfolio"""
        try:
            # Get list of repositories
            repos_response = await self.github_service.get_user_repositories()
            if not repos_response.success:
                return {"error": "Failed to fetch repositories"}
            
            repositories = repos_response.data[:10]  # Limit to top 10
            
            # Calculate growth for each project
            project_metrics = []
            total_growth = 0
            stage_distribution = {stage: 0 for stage in GrowthStage}
            
            for repo in repositories:
                metrics = await self.calculate_project_growth(repo.name)
                if metrics:
                    project_metrics.append({
                        "name": repo.name,
                        "stage": metrics.current_stage.value,
                        "score": metrics.growth_score,
                        "velocity": metrics.velocity,
                        "confidence": metrics.confidence
                    })
                    total_growth += metrics.growth_score
                    stage_distribution[metrics.current_stage] += 1
            
            # Portfolio statistics
            avg_growth = total_growth / len(project_metrics) if project_metrics else 0
            most_active = max(project_metrics, key=lambda p: p["velocity"]) if project_metrics else None
            
            return {
                "total_projects": len(project_metrics),
                "avg_growth_score": avg_growth,
                "stage_distribution": {k.value: v for k, v in stage_distribution.items()},
                "most_active_project": most_active,
                "projects": project_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get portfolio overview: {e}")
            return {"error": str(e)}