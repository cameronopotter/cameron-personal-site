"""
Social media integration service for Twitter, LinkedIn, and RSS feeds.
"""

import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET

from .base import BaseIntegration, APIResponse
from .integration_config import integration_settings

import logging
logger = logging.getLogger(__name__)


class PostType(str, Enum):
    """Social media post types"""
    TWEET = "tweet"
    LINKEDIN = "linkedin"
    BLOG = "blog"
    RSS = "rss"


class EngagementLevel(str, Enum):
    """Engagement level categories"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VIRAL = "viral"


@dataclass
class SocialPost:
    """Social media post data"""
    id: str
    platform: PostType
    content: str
    author: str
    created_at: datetime
    url: Optional[str]
    likes: int
    shares: int
    comments: int
    hashtags: List[str]
    mentions: List[str]
    engagement_rate: float
    tech_relevance_score: float  # 0.0 to 1.0


@dataclass
class SocialMetrics:
    """Social media metrics summary"""
    total_posts: int
    total_engagement: int
    avg_engagement_rate: float
    top_hashtags: List[Dict[str, Any]]
    engagement_by_platform: Dict[str, int]
    posting_frequency: Dict[str, int]  # day of week -> count
    peak_engagement_hours: List[int]
    tech_topic_distribution: Dict[str, float]


@dataclass
class TechTrendAnalysis:
    """Technology trend analysis from social media"""
    trending_topics: List[Dict[str, Any]]
    programming_languages_mentioned: Dict[str, int]
    tech_tools_discussed: Dict[str, int]
    sentiment_analysis: Dict[str, float]  # positive, negative, neutral
    innovation_signals: List[str]  # Emerging tech mentions


class SocialService(BaseIntegration):
    """Social media integration service"""
    
    def __init__(self):
        config = integration_settings.social
        super().__init__(
            name="social",
            base_url="https://api.twitter.com/2",  # Default to Twitter API v2
            timeout=30,
            max_retries=3
        )
        
        self.twitter_bearer_token = config.twitter_bearer_token
        self.linkedin_access_token = config.linkedin_access_token
        self.rss_feeds = config.rss_feeds
        self.max_posts_per_sync = config.max_posts_per_sync
        
        # Tech-related keywords for relevance scoring
        self.tech_keywords = {
            "programming": ["python", "javascript", "java", "golang", "rust", "typescript", "php", "swift"],
            "frameworks": ["react", "vue", "angular", "django", "flask", "express", "nextjs", "svelte"],
            "tools": ["docker", "kubernetes", "git", "vscode", "github", "gitlab", "jenkins", "terraform"],
            "concepts": ["ai", "machine learning", "blockchain", "devops", "microservices", "api", "database", "cloud"],
            "platforms": ["aws", "azure", "gcp", "vercel", "netlify", "heroku", "firebase"]
        }
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers based on the current service"""
        if self.twitter_bearer_token:
            return {"Authorization": f"Bearer {self.twitter_bearer_token}"}
        return {}
    
    async def health_check(self) -> bool:
        """Check social media API health"""
        try:
            if self.twitter_bearer_token:
                response = await self.make_request("GET", "/users/me")
                return response.status_code == 200
            return len(self.rss_feeds) > 0  # At least RSS feeds are configured
        except Exception as e:
            logger.error(f"Social media health check failed: {e}")
            return False
    
    async def get_twitter_posts(self, user_id: Optional[str] = None, count: int = 50) -> APIResponse[List[SocialPost]]:
        """Get Twitter posts (tweets)"""
        try:
            if not self.twitter_bearer_token:
                return APIResponse(
                    success=False,
                    error="Twitter bearer token not configured",
                    service="social"
                )
            
            # Get user's own tweets if no user_id specified
            if not user_id:
                user_response = await self.make_request("GET", "/users/me")
                user_data = user_response.json()["data"]
                user_id = user_data["id"]
            
            params = {
                "max_results": min(count, 100),
                "tweet.fields": "created_at,public_metrics,context_annotations,entities",
                "user.fields": "username"
            }
            
            response = await self.make_request("GET", f"/users/{user_id}/tweets", params=params)
            data = response.json()
            
            posts = []
            for tweet in data.get("data", []):
                # Extract hashtags and mentions
                hashtags = []
                mentions = []
                
                if "entities" in tweet:
                    hashtags = [tag["tag"] for tag in tweet["entities"].get("hashtags", [])]
                    mentions = [mention["username"] for mention in tweet["entities"].get("mentions", [])]
                
                # Calculate engagement metrics
                metrics = tweet.get("public_metrics", {})
                likes = metrics.get("like_count", 0)
                retweets = metrics.get("retweet_count", 0)
                replies = metrics.get("reply_count", 0)
                
                total_engagement = likes + retweets + replies
                engagement_rate = total_engagement / max(metrics.get("impression_count", 1), 1)
                
                # Calculate tech relevance
                tech_relevance = self._calculate_tech_relevance(tweet["text"])
                
                post = SocialPost(
                    id=tweet["id"],
                    platform=PostType.TWEET,
                    content=tweet["text"],
                    author=user_id,  # Would need to look up username
                    created_at=datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00")),
                    url=f"https://twitter.com/user/status/{tweet['id']}",
                    likes=likes,
                    shares=retweets,
                    comments=replies,
                    hashtags=hashtags,
                    mentions=mentions,
                    engagement_rate=engagement_rate,
                    tech_relevance_score=tech_relevance
                )
                posts.append(post)
            
            return APIResponse(
                success=True,
                data=posts,
                service="social",
                metadata={"platform": "twitter", "posts_retrieved": len(posts)}
            )
            
        except Exception as e:
            logger.error(f"Failed to get Twitter posts: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="social"
            )
    
    async def get_linkedin_posts(self, count: int = 50) -> APIResponse[List[SocialPost]]:
        """Get LinkedIn posts"""
        try:
            if not self.linkedin_access_token:
                return APIResponse(
                    success=False,
                    error="LinkedIn access token not configured",
                    service="social"
                )
            
            # LinkedIn API requires different base URL
            linkedin_headers = {"Authorization": f"Bearer {self.linkedin_access_token}"}
            
            # This is a simplified implementation - LinkedIn API is more complex
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.linkedin.com/v2/shares",
                    headers=linkedin_headers,
                    params={"q": "owners", "owners": "urn:li:person:{id}", "count": count}
                )
            
            if response.status_code != 200:
                return APIResponse(
                    success=False,
                    error=f"LinkedIn API error: {response.status_code}",
                    service="social"
                )
            
            data = response.json()
            posts = []
            
            for share in data.get("elements", []):
                # Parse LinkedIn share data (simplified)
                content = share.get("text", {}).get("text", "")
                created_at = datetime.fromtimestamp(share.get("created", {}).get("time", 0) / 1000)
                
                # LinkedIn doesn't provide public engagement metrics easily
                post = SocialPost(
                    id=share.get("id", ""),
                    platform=PostType.LINKEDIN,
                    content=content,
                    author="self",
                    created_at=created_at,
                    url=None,
                    likes=0,  # Would need additional API calls
                    shares=0,
                    comments=0,
                    hashtags=self._extract_hashtags(content),
                    mentions=self._extract_mentions(content),
                    engagement_rate=0.0,
                    tech_relevance_score=self._calculate_tech_relevance(content)
                )
                posts.append(post)
            
            return APIResponse(
                success=True,
                data=posts,
                service="social",
                metadata={"platform": "linkedin", "posts_retrieved": len(posts)}
            )
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn posts: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="social"
            )
    
    async def get_rss_posts(self) -> APIResponse[List[SocialPost]]:
        """Get posts from RSS feeds"""
        try:
            if not self.rss_feeds:
                return APIResponse(
                    success=False,
                    error="No RSS feeds configured",
                    service="social"
                )
            
            all_posts = []
            
            import httpx
            async with httpx.AsyncClient(timeout=30) as client:
                for feed_url in self.rss_feeds:
                    try:
                        response = await client.get(feed_url)
                        if response.status_code != 200:
                            logger.warning(f"Failed to fetch RSS feed: {feed_url}")
                            continue
                        
                        # Parse RSS XML
                        root = ET.fromstring(response.content)
                        
                        # Handle different RSS formats
                        items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
                        
                        for item in items[:10]:  # Limit per feed
                            title = item.find("title") or item.find("{http://www.w3.org/2005/Atom}title")
                            description = item.find("description") or item.find("{http://www.w3.org/2005/Atom}content")
                            link = item.find("link") or item.find("{http://www.w3.org/2005/Atom}link")
                            pub_date = item.find("pubDate") or item.find("{http://www.w3.org/2005/Atom}published")
                            
                            if not title:
                                continue
                            
                            title_text = title.text or ""
                            description_text = description.text if description is not None else ""
                            content = f"{title_text}\n{description_text}"
                            
                            # Parse publication date
                            created_at = datetime.utcnow()
                            if pub_date is not None and pub_date.text:
                                try:
                                    # Handle different date formats
                                    date_str = pub_date.text
                                    if "T" in date_str:
                                        created_at = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                                    else:
                                        from email.utils import parsedate_to_datetime
                                        created_at = parsedate_to_datetime(date_str)
                                except:
                                    pass
                            
                            # Generate unique ID
                            post_id = hashlib.md5(f"{feed_url}{title_text}".encode()).hexdigest()
                            
                            post = SocialPost(
                                id=post_id,
                                platform=PostType.RSS,
                                content=content,
                                author=feed_url,
                                created_at=created_at,
                                url=link.text if link is not None else None,
                                likes=0,
                                shares=0,
                                comments=0,
                                hashtags=self._extract_hashtags(content),
                                mentions=[],
                                engagement_rate=0.0,
                                tech_relevance_score=self._calculate_tech_relevance(content)
                            )
                            all_posts.append(post)
                    
                    except Exception as e:
                        logger.warning(f"Failed to parse RSS feed {feed_url}: {e}")
                        continue
            
            # Sort by creation date and limit
            all_posts.sort(key=lambda p: p.created_at, reverse=True)
            all_posts = all_posts[:self.max_posts_per_sync]
            
            return APIResponse(
                success=True,
                data=all_posts,
                service="social",
                metadata={"platform": "rss", "posts_retrieved": len(all_posts), "feeds_processed": len(self.rss_feeds)}
            )
            
        except Exception as e:
            logger.error(f"Failed to get RSS posts: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="social"
            )
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text.lower())
        return [tag[1:] for tag in hashtags]  # Remove # symbol
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        mention_pattern = r'@\w+'
        mentions = re.findall(mention_pattern, text.lower())
        return [mention[1:] for mention in mentions]  # Remove @ symbol
    
    def _calculate_tech_relevance(self, text: str) -> float:
        """Calculate how relevant a post is to technology"""
        text_lower = text.lower()
        total_keywords = sum(len(keywords) for keywords in self.tech_keywords.values())
        
        matches = 0
        for category, keywords in self.tech_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    matches += 1
        
        relevance = min(matches / total_keywords * 10, 1.0)  # Scale to 0-1
        return relevance
    
    async def get_social_metrics_summary(self, days: int = 30) -> APIResponse[SocialMetrics]:
        """Get comprehensive social media metrics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            all_posts = []
            
            # Collect posts from all platforms
            if self.twitter_bearer_token:
                twitter_response = await self.get_twitter_posts(count=100)
                if twitter_response.success:
                    all_posts.extend(twitter_response.data)
            
            if self.linkedin_access_token:
                linkedin_response = await self.get_linkedin_posts(count=50)
                if linkedin_response.success:
                    all_posts.extend(linkedin_response.data)
            
            if self.rss_feeds:
                rss_response = await self.get_rss_posts()
                if rss_response.success:
                    all_posts.extend(rss_response.data)
            
            # Filter by date
            recent_posts = [p for p in all_posts if p.created_at >= cutoff_date]
            
            if not recent_posts:
                return APIResponse(
                    success=True,
                    data=None,
                    service="social",
                    metadata={"message": "No posts found in time period"}
                )
            
            # Calculate metrics
            total_posts = len(recent_posts)
            total_engagement = sum(p.likes + p.shares + p.comments for p in recent_posts)
            avg_engagement_rate = sum(p.engagement_rate for p in recent_posts) / total_posts
            
            # Analyze hashtags
            hashtag_counts = {}
            for post in recent_posts:
                for tag in post.hashtags:
                    hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
            
            top_hashtags = [
                {"tag": tag, "count": count, "percentage": (count / total_posts) * 100}
                for tag, count in sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Engagement by platform
            engagement_by_platform = {}
            for post in recent_posts:
                platform = post.platform.value
                engagement = post.likes + post.shares + post.comments
                engagement_by_platform[platform] = engagement_by_platform.get(platform, 0) + engagement
            
            # Posting frequency by day of week
            posting_frequency = {}
            for post in recent_posts:
                day_name = post.created_at.strftime("%A")
                posting_frequency[day_name] = posting_frequency.get(day_name, 0) + 1
            
            # Tech topic distribution
            tech_topic_counts = {}
            for post in recent_posts:
                for category, keywords in self.tech_keywords.items():
                    for keyword in keywords:
                        if keyword in post.content.lower():
                            tech_topic_counts[category] = tech_topic_counts.get(category, 0) + 1
            
            total_tech_mentions = sum(tech_topic_counts.values())
            tech_topic_distribution = {
                category: (count / total_tech_mentions) * 100 if total_tech_mentions > 0 else 0
                for category, count in tech_topic_counts.items()
            }
            
            metrics = SocialMetrics(
                total_posts=total_posts,
                total_engagement=total_engagement,
                avg_engagement_rate=avg_engagement_rate,
                top_hashtags=top_hashtags,
                engagement_by_platform=engagement_by_platform,
                posting_frequency=posting_frequency,
                peak_engagement_hours=[9, 12, 15, 18, 21],  # Would need hourly analysis
                tech_topic_distribution=tech_topic_distribution
            )
            
            return APIResponse(
                success=True,
                data=metrics,
                service="social",
                metadata={"analysis_period_days": days, "posts_analyzed": total_posts}
            )
            
        except Exception as e:
            logger.error(f"Failed to get social metrics: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="social"
            )
    
    async def analyze_tech_trends(self, days: int = 7) -> APIResponse[TechTrendAnalysis]:
        """Analyze technology trends from social media"""
        try:
            # Get recent posts
            all_posts = []
            
            if self.twitter_bearer_token:
                twitter_response = await self.get_twitter_posts(count=200)
                if twitter_response.success:
                    all_posts.extend(twitter_response.data)
            
            if self.rss_feeds:
                rss_response = await self.get_rss_posts()
                if rss_response.success:
                    all_posts.extend(rss_response.data)
            
            # Filter by date and tech relevance
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            tech_posts = [
                p for p in all_posts 
                if p.created_at >= cutoff_date and p.tech_relevance_score > 0.3
            ]
            
            if not tech_posts:
                return APIResponse(
                    success=False,
                    error="No tech-relevant posts found",
                    service="social"
                )
            
            # Analyze trending topics
            topic_mentions = {}
            language_mentions = {}
            tool_mentions = {}
            
            for post in tech_posts:
                content_lower = post.content.lower()
                
                # Count programming languages
                for lang in self.tech_keywords["programming"]:
                    if lang in content_lower:
                        language_mentions[lang] = language_mentions.get(lang, 0) + 1
                
                # Count tools
                for tool in self.tech_keywords["tools"]:
                    if tool in content_lower:
                        tool_mentions[tool] = tool_mentions.get(tool, 0) + 1
                
                # Count general topics
                for concept in self.tech_keywords["concepts"]:
                    if concept in content_lower:
                        topic_mentions[concept] = topic_mentions.get(concept, 0) + 1
            
            # Sort trending topics
            trending_topics = [
                {
                    "topic": topic,
                    "mentions": count,
                    "trend_score": count / len(tech_posts),
                    "category": "trending"
                }
                for topic, count in sorted(topic_mentions.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Simple sentiment analysis (keyword-based)
            positive_keywords = ["love", "awesome", "great", "amazing", "excited", "breakthrough"]
            negative_keywords = ["hate", "terrible", "awful", "frustrated", "broken", "deprecated"]
            
            positive_count = 0
            negative_count = 0
            
            for post in tech_posts:
                content_lower = post.content.lower()
                positive_count += sum(1 for word in positive_keywords if word in content_lower)
                negative_count += sum(1 for word in negative_keywords if word in content_lower)
            
            total_sentiment = positive_count + negative_count
            sentiment_analysis = {
                "positive": (positive_count / total_sentiment) if total_sentiment > 0 else 0.5,
                "negative": (negative_count / total_sentiment) if total_sentiment > 0 else 0.5,
                "neutral": max(0, 1.0 - (positive_count + negative_count) / total_sentiment) if total_sentiment > 0 else 0
            }
            
            # Innovation signals (emerging tech)
            innovation_keywords = ["quantum", "edge computing", "webassembly", "rust", "deno", "serverless"]
            innovation_signals = [
                keyword for keyword in innovation_keywords
                if any(keyword in post.content.lower() for post in tech_posts)
            ]
            
            analysis = TechTrendAnalysis(
                trending_topics=trending_topics,
                programming_languages_mentioned=language_mentions,
                tech_tools_discussed=tool_mentions,
                sentiment_analysis=sentiment_analysis,
                innovation_signals=innovation_signals
            )
            
            return APIResponse(
                success=True,
                data=analysis,
                service="social",
                metadata={
                    "analysis_period_days": days,
                    "tech_posts_analyzed": len(tech_posts),
                    "total_posts_scanned": len(all_posts)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze tech trends: {e}")
            return APIResponse(
                success=False,
                error=str(e),
                service="social"
            )