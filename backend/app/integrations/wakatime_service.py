"""
WakaTime API integration service for coding time tracking and productivity analysis.
"""

from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .base import BaseIntegration, APIResponse
from .integration_config import integration_settings

import logging
logger = logging.getLogger(__name__)


class ProductivityLevel(str, Enum):
    """Productivity level categories"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class CodingSession:
    """Individual coding session data"""
    start_time: datetime
    end_time: datetime
    duration_seconds: int
    project: Optional[str]
    language: Optional[str]
    editor: Optional[str]
    operating_system: Optional[str]
    lines_added: Optional[int]
    lines_removed: Optional[int]


@dataclass
class DailySummary:
    """Daily coding activity summary"""
    date: date
    total_seconds: int
    projects: Dict[str, int]  # project_name -> seconds
    languages: Dict[str, int]  # language -> seconds
    editors: Dict[str, int]  # editor -> seconds
    categories: Dict[str, int]  # category -> seconds
    operating_systems: Dict[str, int]  # os -> seconds
    productivity_score: float  # 0.0 to 1.0


@dataclass
class WeeklySummary:
    """Weekly coding activity summary"""
    start_date: date
    end_date: date
    total_seconds: int
    daily_average_seconds: int
    most_productive_day: date
    least_productive_day: date
    top_projects: List[Dict[str, Any]]
    top_languages: List[Dict[str, Any]]
    productivity_trend: str  # increasing, decreasing, stable


@dataclass
class ProductivityAnalysis:
    """Comprehensive productivity analysis"""
    current_level: ProductivityLevel
    weekly_hours: float
    monthly_hours: float
    productivity_score: float  # 0.0 to 1.0
    focus_score: float  # 0.0 to 1.0 (based on project switching)
    consistency_score: float  # 0.0 to 1.0 (regularity of coding)
    growth_velocity: float  # Lines of code per hour
    project_diversity: int  # Number of different projects
    language_mastery: Dict[str, float]  # language -> mastery score
    best_coding_hours: List[int]  # Hours of day with highest productivity
    

class WakaTimeService(BaseIntegration):
    """WakaTime API integration service"""
    
    def __init__(self):
        config = integration_settings.wakatime
        super().__init__(
            name="wakatime",
            base_url=config.base_url,
            api_key=config.api_key,
            timeout=30,
            max_retries=3
        )
        
        self.username = config.username
        self.include_projects = config.include_projects
        self.exclude_projects = config.exclude_projects
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get WakaTime authentication headers"""
        return {
            "Authorization": f"Bearer {self.api_key}"
        }
    
    async def health_check(self) -> bool:
        """Check WakaTime API health"""
        try:
            response = await self.make_request("GET", "/users/current")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"WakaTime health check failed: {e}")
            return False
    
    async def get_user_info(self) -> APIResponse[Dict[str, Any]]:
        """Get current user information"""
        try:
            response = await self.make_request("GET", "/users/current")
            data = response.json()["data"]
            
            user_info = {
                "id": data.get("id"),
                "username": data.get("username"),
                "full_name": data.get("full_name"),
                "email": data.get("email"),
                "timezone": data.get("timezone"),
                "last_heartbeat": data.get("last_heartbeat_at"),
                "created_at": data.get("created_at"),
                "modified_at": data.get("modified_at")
            }
            
            return APIResponse(
                success=True,
                data=user_info,
                service="wakatime"
            )
            
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="wakatime"
            )
    
    async def get_daily_summary(self, target_date: Optional[date] = None) -> APIResponse[DailySummary]:
        """Get daily coding summary"""
        try:
            target_date = target_date or date.today()
            date_str = target_date.isoformat()
            
            response = await self.make_request("GET", f"/users/current/summaries", params={
                "start": date_str,
                "end": date_str
            })
            
            data = response.json()["data"]
            
            if not data:
                return APIResponse(
                    success=True,
                    data=None,
                    service="wakatime",
                    metadata={"message": "No data for date", "date": date_str}
                )
            
            day_data = data[0]
            
            # Parse projects
            projects = {
                p["name"]: p["total_seconds"] 
                for p in day_data.get("projects", [])
                if not self.include_projects or p["name"] in self.include_projects
                if p["name"] not in self.exclude_projects
            }
            
            # Parse languages
            languages = {
                l["name"]: l["total_seconds"]
                for l in day_data.get("languages", [])
            }
            
            # Parse editors
            editors = {
                e["name"]: e["total_seconds"]
                for e in day_data.get("editors", [])
            }
            
            # Parse categories
            categories = {
                c["name"]: c["total_seconds"]
                for c in day_data.get("categories", [])
            }
            
            # Parse operating systems
            operating_systems = {
                os["name"]: os["total_seconds"]
                for os in day_data.get("operating_systems", [])
            }
            
            # Calculate productivity score
            total_seconds = day_data.get("grand_total", {}).get("total_seconds", 0)
            productivity_score = min(total_seconds / (8 * 3600), 1.0)  # Normalized to 8-hour workday
            
            summary = DailySummary(
                date=target_date,
                total_seconds=total_seconds,
                projects=projects,
                languages=languages,
                editors=editors,
                categories=categories,
                operating_systems=operating_systems,
                productivity_score=productivity_score
            )
            
            return APIResponse(
                success=True,
                data=summary,
                service="wakatime",
                metadata={"date": date_str, "total_hours": total_seconds / 3600}
            )
            
        except Exception as e:
            logger.error(f"Failed to get daily summary: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="wakatime"
            )
    
    async def get_weekly_summary(self, start_date: Optional[date] = None) -> APIResponse[WeeklySummary]:
        """Get weekly coding summary"""
        try:
            if not start_date:
                # Get start of current week (Monday)
                today = date.today()
                start_date = today - timedelta(days=today.weekday())
            
            end_date = start_date + timedelta(days=6)
            
            response = await self.make_request("GET", f"/users/current/summaries", params={
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            })
            
            data = response.json()["data"]
            
            if not data:
                return APIResponse(
                    success=True,
                    data=None,
                    service="wakatime",
                    metadata={"message": "No data for week"}
                )
            
            # Aggregate weekly data
            total_seconds = 0
            daily_seconds = {}
            all_projects = {}
            all_languages = {}
            
            for day_data in data:
                day_total = day_data.get("grand_total", {}).get("total_seconds", 0)
                day_date = datetime.fromisoformat(day_data["range"]["date"]).date()
                
                daily_seconds[day_date] = day_total
                total_seconds += day_total
                
                # Aggregate projects
                for project in day_data.get("projects", []):
                    name = project["name"]
                    if name in self.exclude_projects:
                        continue
                    if self.include_projects and name not in self.include_projects:
                        continue
                        
                    all_projects[name] = all_projects.get(name, 0) + project["total_seconds"]
                
                # Aggregate languages
                for language in day_data.get("languages", []):
                    name = language["name"]
                    all_languages[name] = all_languages.get(name, 0) + language["total_seconds"]
            
            # Calculate statistics
            daily_average = total_seconds / 7
            
            most_productive_day = max(daily_seconds.items(), key=lambda x: x[1])[0] if daily_seconds else start_date
            least_productive_day = min(daily_seconds.items(), key=lambda x: x[1])[0] if daily_seconds else start_date
            
            # Sort top projects and languages
            top_projects = [
                {"name": name, "total_seconds": seconds, "percentage": (seconds / total_seconds) * 100}
                for name, seconds in sorted(all_projects.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            top_languages = [
                {"name": name, "total_seconds": seconds, "percentage": (seconds / total_seconds) * 100}
                for name, seconds in sorted(all_languages.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            # Calculate productivity trend
            first_half = sum(list(daily_seconds.values())[:3])
            second_half = sum(list(daily_seconds.values())[4:])
            
            if second_half > first_half * 1.1:
                productivity_trend = "increasing"
            elif second_half < first_half * 0.9:
                productivity_trend = "decreasing"
            else:
                productivity_trend = "stable"
            
            summary = WeeklySummary(
                start_date=start_date,
                end_date=end_date,
                total_seconds=total_seconds,
                daily_average_seconds=int(daily_average),
                most_productive_day=most_productive_day,
                least_productive_day=least_productive_day,
                top_projects=top_projects,
                top_languages=top_languages,
                productivity_trend=productivity_trend
            )
            
            return APIResponse(
                success=True,
                data=summary,
                service="wakatime",
                metadata={
                    "week": f"{start_date} to {end_date}",
                    "total_hours": total_seconds / 3600
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get weekly summary: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="wakatime"
            )
    
    async def get_productivity_analysis(self, days: int = 30) -> APIResponse[ProductivityAnalysis]:
        """Get comprehensive productivity analysis"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days-1)
            
            response = await self.make_request("GET", f"/users/current/summaries", params={
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            })
            
            data = response.json()["data"]
            
            if not data:
                return APIResponse(
                    success=False,
                    error="No data available for analysis period",
                    service="wakatime"
                )
            
            # Aggregate data
            total_seconds = 0
            daily_totals = []
            hourly_distribution = [0] * 24
            all_projects = {}
            all_languages = {}
            project_switches = 0
            coding_days = 0
            
            for day_data in data:
                day_total = day_data.get("grand_total", {}).get("total_seconds", 0)
                daily_totals.append(day_total)
                total_seconds += day_total
                
                if day_total > 0:
                    coding_days += 1
                
                # Analyze hourly distribution (if available)
                # This would require additional API calls to get hourly data
                
                # Count projects per day for focus score
                day_projects = len([p for p in day_data.get("projects", []) if p["total_seconds"] > 300])  # 5+ minutes
                project_switches += max(0, day_projects - 1)
                
                # Aggregate project time
                for project in day_data.get("projects", []):
                    name = project["name"]
                    if name not in self.exclude_projects:
                        all_projects[name] = all_projects.get(name, 0) + project["total_seconds"]
                
                # Aggregate language time
                for language in day_data.get("languages", []):
                    name = language["name"]
                    all_languages[name] = all_languages.get(name, 0) + language["total_seconds"]
            
            # Calculate metrics
            weekly_hours = (total_seconds / days * 7) / 3600
            monthly_hours = (total_seconds / days * 30) / 3600
            
            # Productivity score (0-1 based on daily average vs 4-hour target)
            daily_average_hours = (total_seconds / days) / 3600
            productivity_score = min(daily_average_hours / 4, 1.0)
            
            # Focus score (lower project switching = higher focus)
            avg_switches_per_day = project_switches / max(coding_days, 1)
            focus_score = max(0, 1.0 - (avg_switches_per_day / 5))  # Normalize to 5 switches
            
            # Consistency score (regularity of coding)
            coding_days_ratio = coding_days / days
            consistency_score = coding_days_ratio
            
            # Calculate language mastery (based on time spent and frequency)
            language_mastery = {}
            total_language_time = sum(all_languages.values())
            for language, time_spent in all_languages.items():
                if total_language_time > 0:
                    mastery = (time_spent / total_language_time) * consistency_score
                    language_mastery[language] = min(mastery, 1.0)
            
            # Determine current productivity level
            if productivity_score >= 0.8:
                current_level = ProductivityLevel.VERY_HIGH
            elif productivity_score >= 0.6:
                current_level = ProductivityLevel.HIGH
            elif productivity_score >= 0.4:
                current_level = ProductivityLevel.MODERATE
            elif productivity_score >= 0.2:
                current_level = ProductivityLevel.LOW
            else:
                current_level = ProductivityLevel.VERY_LOW
            
            # Growth velocity (simplified - would need more detailed commit data)
            growth_velocity = daily_average_hours * 50  # Rough estimate: 50 LoC per hour
            
            # Best coding hours (would need hourly API data)
            best_coding_hours = [9, 10, 14, 15, 16]  # Default productive hours
            
            analysis = ProductivityAnalysis(
                current_level=current_level,
                weekly_hours=weekly_hours,
                monthly_hours=monthly_hours,
                productivity_score=productivity_score,
                focus_score=focus_score,
                consistency_score=consistency_score,
                growth_velocity=growth_velocity,
                project_diversity=len(all_projects),
                language_mastery=language_mastery,
                best_coding_hours=best_coding_hours
            )
            
            return APIResponse(
                success=True,
                data=analysis,
                service="wakatime",
                metadata={
                    "analysis_period_days": days,
                    "total_hours": total_seconds / 3600,
                    "coding_days": coding_days
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get productivity analysis: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="wakatime"
            )
    
    async def get_project_growth_data(self, project_name: str, days: int = 30) -> Dict[str, Any]:
        """Get growth data for a specific project"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days-1)
            
            response = await self.make_request("GET", f"/users/current/summaries", params={
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "project": project_name
            })
            
            data = response.json()["data"]
            
            if not data:
                return {"error": f"No data for project {project_name}"}
            
            # Analyze project data
            daily_times = []
            total_time = 0
            languages_used = {}
            
            for day_data in data:
                day_total = 0
                for project in day_data.get("projects", []):
                    if project["name"] == project_name:
                        day_total = project["total_seconds"]
                        break
                
                daily_times.append({
                    "date": day_data["range"]["date"],
                    "seconds": day_total
                })
                total_time += day_total
                
                # Track languages for this project
                for language in day_data.get("languages", []):
                    languages_used[language["name"]] = languages_used.get(language["name"], 0) + language["total_seconds"]
            
            # Calculate growth metrics
            first_week = sum(d["seconds"] for d in daily_times[:7])
            last_week = sum(d["seconds"] for d in daily_times[-7:])
            
            growth_rate = ((last_week - first_week) / max(first_week, 1)) * 100 if first_week > 0 else 0
            
            # Velocity (hours per week)
            avg_weekly_hours = (total_time / days * 7) / 3600
            
            return {
                "project": project_name,
                "total_time_hours": total_time / 3600,
                "daily_breakdown": daily_times,
                "growth_rate_percent": growth_rate,
                "avg_weekly_hours": avg_weekly_hours,
                "primary_languages": sorted(
                    languages_used.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:3],
                "analysis_period_days": days
            }
            
        except Exception as e:
            logger.error(f"Failed to get project growth data: {e}")
            return {"error": str(e)}