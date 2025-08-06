"""
GitHub API integration service for repository and activity data.
"""

import hmac
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from pydantic import BaseModel

from .base import BaseIntegration, WebhookHandler, APIResponse, IntegrationError
from .integration_config import integration_settings

import logging
logger = logging.getLogger(__name__)


@dataclass
class GitHubRepository:
    """GitHub repository data model"""
    id: int
    name: str
    full_name: str
    description: Optional[str]
    language: Optional[str]
    stars: int
    forks: int
    size: int
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    is_private: bool
    topics: List[str]
    license: Optional[str]
    default_branch: str


@dataclass
class GitHubCommit:
    """GitHub commit data model"""
    sha: str
    message: str
    author_name: str
    author_email: str
    committer_name: str
    committer_email: str
    committed_at: datetime
    additions: int
    deletions: int
    files_changed: int
    repository: str


@dataclass
class GitHubLanguageStats:
    """GitHub repository language statistics"""
    repository: str
    languages: Dict[str, int]
    total_bytes: int
    primary_language: Optional[str]


@dataclass
class GitHubActivity:
    """GitHub activity summary"""
    commits_today: int
    commits_this_week: int
    commits_this_month: int
    repositories_updated: List[str]
    lines_added: int
    lines_deleted: int
    active_languages: List[str]
    last_activity: Optional[datetime]


class GitHubWebhookHandler(WebhookHandler):
    """GitHub webhook handler for real-time events"""
    
    def __init__(self, secret: str):
        self.secret = secret
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature"""
        if not self.secret:
            return False
        
        expected_signature = "sha256=" + hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    async def handle_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Handle GitHub webhook payload"""
        try:
            event_type = headers.get('X-GitHub-Event', '')
            
            if event_type == 'push':
                await self._handle_push_event(payload)
            elif event_type == 'pull_request':
                await self._handle_pull_request_event(payload)
            elif event_type == 'issues':
                await self._handle_issue_event(payload)
            elif event_type == 'release':
                await self._handle_release_event(payload)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle GitHub webhook: {e}")
            return False
    
    async def _handle_push_event(self, payload: Dict[str, Any]):
        """Handle push event"""
        repository = payload.get('repository', {}).get('name', 'unknown')
        commits = payload.get('commits', [])
        
        logger.info(f"Push event: {len(commits)} commits to {repository}")
        
        # Emit real-time event for garden updates
        from ..websockets.manager import websocket_manager
        await websocket_manager.broadcast({
            'type': 'commit_pushed',
            'repository': repository,
            'commit_count': len(commits),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def _handle_pull_request_event(self, payload: Dict[str, Any]):
        """Handle pull request event"""
        action = payload.get('action', '')
        pr = payload.get('pull_request', {})
        repository = payload.get('repository', {}).get('name', 'unknown')
        
        logger.info(f"PR event: {action} on {repository}")
    
    async def _handle_issue_event(self, payload: Dict[str, Any]):
        """Handle issue event"""
        action = payload.get('action', '')
        issue = payload.get('issue', {})
        repository = payload.get('repository', {}).get('name', 'unknown')
        
        logger.info(f"Issue event: {action} on {repository}")
    
    async def _handle_release_event(self, payload: Dict[str, Any]):
        """Handle release event"""
        action = payload.get('action', '')
        release = payload.get('release', {})
        repository = payload.get('repository', {}).get('name', 'unknown')
        
        logger.info(f"Release event: {action} on {repository}")


class GitHubService(BaseIntegration):
    """GitHub API integration service"""
    
    def __init__(self):
        config = integration_settings.github
        super().__init__(
            name="github",
            base_url=config.base_url,
            api_key=config.token,
            timeout=30,
            max_retries=3
        )
        
        self.username = config.username
        self.repositories = config.repositories or []
        self.webhook_handler = GitHubWebhookHandler(config.webhook_secret)
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get GitHub authentication headers"""
        return {
            "Authorization": f"token {self.api_key}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def health_check(self) -> bool:
        """Check GitHub API health"""
        try:
            response = await self.make_request("GET", "/rate_limit")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"GitHub health check failed: {e}")
            return False
    
    async def get_user_repositories(self, include_private: bool = False) -> APIResponse[List[GitHubRepository]]:
        """Get user's repositories"""
        try:
            params = {
                "type": "all" if include_private else "public",
                "sort": "updated",
                "per_page": 100
            }
            
            response = await self.make_request("GET", f"/users/{self.username}/repos", params=params)
            repos_data = response.json()
            
            repositories = []
            for repo_data in repos_data:
                repo = GitHubRepository(
                    id=repo_data["id"],
                    name=repo_data["name"],
                    full_name=repo_data["full_name"],
                    description=repo_data.get("description"),
                    language=repo_data.get("language"),
                    stars=repo_data["stargazers_count"],
                    forks=repo_data["forks_count"],
                    size=repo_data["size"],
                    created_at=datetime.fromisoformat(repo_data["created_at"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(repo_data["updated_at"].replace("Z", "+00:00")),
                    pushed_at=datetime.fromisoformat(repo_data["pushed_at"].replace("Z", "+00:00")),
                    is_private=repo_data["private"],
                    topics=repo_data.get("topics", []),
                    license=repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
                    default_branch=repo_data["default_branch"]
                )
                repositories.append(repo)
            
            return APIResponse(
                success=True,
                data=repositories,
                service="github",
                metadata={"total_repos": len(repositories)}
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch repositories: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="github"
            )
    
    async def get_repository_commits(
        self, 
        repo_name: str, 
        since: Optional[datetime] = None,
        limit: int = 50
    ) -> APIResponse[List[GitHubCommit]]:
        """Get repository commits"""
        try:
            params = {
                "per_page": min(limit, 100),
                "author": self.username
            }
            
            if since:
                params["since"] = since.isoformat()
            
            response = await self.make_request("GET", f"/repos/{self.username}/{repo_name}/commits", params=params)
            commits_data = response.json()
            
            commits = []
            for commit_data in commits_data:
                commit_detail = await self._get_commit_details(repo_name, commit_data["sha"])
                
                commit = GitHubCommit(
                    sha=commit_data["sha"],
                    message=commit_data["commit"]["message"],
                    author_name=commit_data["commit"]["author"]["name"],
                    author_email=commit_data["commit"]["author"]["email"],
                    committer_name=commit_data["commit"]["committer"]["name"],
                    committer_email=commit_data["commit"]["committer"]["email"],
                    committed_at=datetime.fromisoformat(
                        commit_data["commit"]["committer"]["date"].replace("Z", "+00:00")
                    ),
                    additions=commit_detail.get("additions", 0),
                    deletions=commit_detail.get("deletions", 0),
                    files_changed=len(commit_detail.get("files", [])),
                    repository=repo_name
                )
                commits.append(commit)
            
            return APIResponse(
                success=True,
                data=commits,
                service="github",
                metadata={"repository": repo_name, "commit_count": len(commits)}
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch commits for {repo_name}: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="github"
            )
    
    async def _get_commit_details(self, repo_name: str, sha: str) -> Dict[str, Any]:
        """Get detailed commit information"""
        try:
            response = await self.make_request("GET", f"/repos/{self.username}/{repo_name}/commits/{sha}")
            return response.json().get("stats", {})
        except Exception as e:
            logger.warning(f"Failed to get commit details for {sha}: {e}")
            return {}
    
    async def get_repository_languages(self, repo_name: str) -> APIResponse[GitHubLanguageStats]:
        """Get repository language statistics"""
        try:
            response = await self.make_request("GET", f"/repos/{self.username}/{repo_name}/languages")
            languages_data = response.json()
            
            total_bytes = sum(languages_data.values())
            primary_language = max(languages_data.items(), key=lambda x: x[1])[0] if languages_data else None
            
            stats = GitHubLanguageStats(
                repository=repo_name,
                languages=languages_data,
                total_bytes=total_bytes,
                primary_language=primary_language
            )
            
            return APIResponse(
                success=True,
                data=stats,
                service="github",
                metadata={"repository": repo_name, "language_count": len(languages_data)}
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch languages for {repo_name}: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="github"
            )
    
    async def get_user_activity_summary(self, days: int = 30) -> APIResponse[GitHubActivity]:
        """Get user activity summary"""
        try:
            since = datetime.utcnow() - timedelta(days=days)
            
            # Get all repositories
            repos_response = await self.get_user_repositories()
            if not repos_response.success:
                raise IntegrationError("Failed to fetch repositories", "github")
            
            repositories = repos_response.data
            
            # Aggregate activity data
            total_commits = 0
            commits_today = 0
            commits_this_week = 0 
            commits_this_month = 0
            total_additions = 0
            total_deletions = 0
            active_languages = set()
            repositories_updated = []
            last_activity = None
            
            today = datetime.utcnow().date()
            week_ago = datetime.utcnow() - timedelta(days=7)
            month_ago = datetime.utcnow() - timedelta(days=30)
            
            for repo in repositories[:10]:  # Limit to avoid rate limits
                commits_response = await self.get_repository_commits(repo.name, since, limit=30)
                if commits_response.success:
                    repo_commits = commits_response.data
                    
                    if repo_commits:
                        repositories_updated.append(repo.name)
                        
                        for commit in repo_commits:
                            total_commits += 1
                            total_additions += commit.additions
                            total_deletions += commit.deletions
                            
                            if commit.committed_at.date() == today:
                                commits_today += 1
                            if commit.committed_at >= week_ago:
                                commits_this_week += 1
                            if commit.committed_at >= month_ago:
                                commits_this_month += 1
                            
                            if not last_activity or commit.committed_at > last_activity:
                                last_activity = commit.committed_at
                
                # Get repository languages
                if repo.language:
                    active_languages.add(repo.language)
            
            activity = GitHubActivity(
                commits_today=commits_today,
                commits_this_week=commits_this_week,
                commits_this_month=commits_this_month,
                repositories_updated=repositories_updated,
                lines_added=total_additions,
                lines_deleted=total_deletions,
                active_languages=list(active_languages),
                last_activity=last_activity
            )
            
            return APIResponse(
                success=True,
                data=activity,
                service="github",
                metadata={
                    "analysis_period_days": days,
                    "repositories_analyzed": len(repositories_updated)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get activity summary: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="github"
            )
    
    async def calculate_growth_metrics(self, repo_name: str) -> Dict[str, Any]:
        """Calculate growth metrics for a repository"""
        try:
            # Get repository details
            repos_response = await self.get_user_repositories()
            if not repos_response.success:
                return {}
            
            repo = next((r for r in repos_response.data if r.name == repo_name), None)
            if not repo:
                return {}
            
            # Get recent commits
            month_ago = datetime.utcnow() - timedelta(days=30)
            commits_response = await self.get_repository_commits(repo_name, month_ago, 100)
            
            if not commits_response.success:
                return {}
            
            commits = commits_response.data
            
            # Calculate metrics
            commit_frequency = len(commits) / 30  # commits per day
            
            total_changes = sum(c.additions + c.deletions for c in commits)
            avg_changes_per_commit = total_changes / len(commits) if commits else 0
            
            # Repository maturity (based on age and activity)
            repo_age_days = (datetime.utcnow() - repo.created_at).days
            maturity_score = min(repo_age_days / 365, 1.0)  # 0-1 scale
            
            # Growth velocity
            recent_commits = [c for c in commits if c.committed_at >= datetime.utcnow() - timedelta(days=7)]
            velocity_score = len(recent_commits) / 7  # commits per day this week
            
            return {
                "repository": repo_name,
                "commit_frequency": commit_frequency,
                "avg_changes_per_commit": avg_changes_per_commit,
                "maturity_score": maturity_score,
                "velocity_score": velocity_score,
                "stars": repo.stars,
                "forks": repo.forks,
                "size_kb": repo.size,
                "primary_language": repo.language,
                "last_updated": repo.updated_at.isoformat(),
                "total_commits_30d": len(commits)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate growth metrics for {repo_name}: {e}")
            return {}