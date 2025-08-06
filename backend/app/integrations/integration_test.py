"""
Comprehensive integration test suite for all external API services.
"""

import asyncio
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import all integration services
from .github_service import GitHubService
from .spotify_service import SpotifyService
from .weather_service import WeatherService
from .wakatime_service import WakaTimeService
from .social_service import SocialService
from .growth_engine import GrowthEngine
from .mood_engine import MoodEngine
from .analytics_processor import AnalyticsProcessor
from .websocket_manager import websocket_manager
from .cache_manager import cache_manager
from .task_scheduler import task_scheduler
from .rate_limiter import rate_limiter
from .privacy_manager import privacy_manager
from .integration_config import integration_settings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntegrationTester:
    """Comprehensive integration testing suite"""
    
    def __init__(self):
        self.test_results = {}
        self.services = {}
        self.engines = {}
        self.infrastructure = {}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        logger.info("Starting comprehensive integration test suite")
        
        # Initialize all services
        await self._initialize_services()
        
        # Test individual services
        await self._test_external_services()
        
        # Test data processors
        await self._test_data_processors()
        
        # Test infrastructure components
        await self._test_infrastructure()
        
        # Test real-time pipeline
        await self._test_real_time_pipeline()
        
        # Generate summary report
        self._generate_summary_report()
        
        logger.info("Integration test suite completed")
        return self.test_results
    
    async def _initialize_services(self):
        """Initialize all services for testing"""
        logger.info("Initializing services...")
        
        try:
            # External API services
            self.services['github'] = GitHubService()
            self.services['spotify'] = SpotifyService()
            self.services['weather'] = WeatherService()
            self.services['wakatime'] = WakaTimeService()
            self.services['social'] = SocialService()
            
            # Data processors
            self.engines['growth'] = GrowthEngine()
            self.engines['mood'] = MoodEngine()
            self.engines['analytics'] = AnalyticsProcessor()
            
            # Infrastructure
            self.infrastructure['cache'] = cache_manager
            self.infrastructure['scheduler'] = task_scheduler
            self.infrastructure['rate_limiter'] = rate_limiter
            self.infrastructure['privacy'] = privacy_manager
            self.infrastructure['websocket'] = websocket_manager
            
            # Initialize cache manager
            await cache_manager.initialize()
            
            logger.info("All services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            self.test_results['initialization'] = {'status': 'failed', 'error': str(e)}
    
    async def _test_external_services(self):
        """Test all external API services"""
        logger.info("Testing external API services...")
        
        # Test GitHub service
        await self._test_github_service()
        
        # Test Weather service
        await self._test_weather_service()
        
        # Test Spotify service (if configured)
        if integration_settings.spotify.is_configured:
            await self._test_spotify_service()
        else:
            self.test_results['spotify'] = {'status': 'skipped', 'reason': 'not_configured'}
        
        # Test WakaTime service (if configured)
        if integration_settings.wakatime.is_configured:
            await self._test_wakatime_service()
        else:
            self.test_results['wakatime'] = {'status': 'skipped', 'reason': 'not_configured'}
        
        # Test Social service (if configured)
        if integration_settings.social.is_configured:
            await self._test_social_service()
        else:
            self.test_results['social'] = {'status': 'skipped', 'reason': 'not_configured'}
    
    async def _test_github_service(self):
        """Test GitHub API service"""
        logger.info("Testing GitHub service...")
        
        test_result = {
            'status': 'unknown',
            'tests': [],
            'errors': []
        }
        
        try:
            github = self.services['github']
            
            # Test health check
            health_ok = await github.health_check()
            test_result['tests'].append({
                'name': 'health_check',
                'status': 'passed' if health_ok else 'failed'
            })
            
            if not health_ok:
                test_result['errors'].append("Health check failed")
                test_result['status'] = 'failed'
                self.test_results['github'] = test_result
                return
            
            # Test repository fetching
            try:
                repos_response = await github.get_user_repositories()
                test_result['tests'].append({
                    'name': 'get_repositories',
                    'status': 'passed' if repos_response.success else 'failed',
                    'data_count': len(repos_response.data) if repos_response.success else 0
                })
                
                if repos_response.success and repos_response.data:
                    # Test commit fetching for first repository
                    first_repo = repos_response.data[0]
                    commits_response = await github.get_repository_commits(first_repo.name, limit=5)
                    test_result['tests'].append({
                        'name': 'get_commits',
                        'status': 'passed' if commits_response.success else 'failed',
                        'repo_tested': first_repo.name
                    })
                    
                    # Test language stats
                    lang_response = await github.get_repository_languages(first_repo.name)
                    test_result['tests'].append({
                        'name': 'get_languages',
                        'status': 'passed' if lang_response.success else 'failed'
                    })
            
            except Exception as e:
                test_result['errors'].append(f"Repository tests failed: {e}")
                test_result['tests'].append({
                    'name': 'repository_operations',
                    'status': 'failed'
                })
            
            # Test activity summary
            try:
                activity_response = await github.get_user_activity_summary(7)
                test_result['tests'].append({
                    'name': 'get_activity_summary',
                    'status': 'passed' if activity_response.success else 'failed'
                })
            except Exception as e:
                test_result['errors'].append(f"Activity summary failed: {e}")
            
            # Determine overall status
            passed_tests = sum(1 for t in test_result['tests'] if t['status'] == 'passed')
            total_tests = len(test_result['tests'])
            
            if passed_tests == total_tests:
                test_result['status'] = 'passed'
            elif passed_tests > 0:
                test_result['status'] = 'partial'
            else:
                test_result['status'] = 'failed'
                
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f"GitHub service test failed: {e}")
        
        self.test_results['github'] = test_result
        logger.info(f"GitHub service test completed: {test_result['status']}")
    
    async def _test_weather_service(self):
        """Test Weather API service"""
        logger.info("Testing Weather service...")
        
        test_result = {
            'status': 'unknown',
            'tests': [],
            'errors': []
        }
        
        try:
            weather = self.services['weather']
            
            # Test health check
            health_ok = await weather.health_check()
            test_result['tests'].append({
                'name': 'health_check',
                'status': 'passed' if health_ok else 'failed'
            })
            
            if not health_ok:
                test_result['errors'].append("Weather API health check failed")
                test_result['status'] = 'failed'
                self.test_results['weather'] = test_result
                return
            
            # Test current weather
            try:
                current_response = await weather.get_current_weather()
                test_result['tests'].append({
                    'name': 'get_current_weather',
                    'status': 'passed' if current_response.success else 'failed'
                })
                
                if current_response.success:
                    current_weather = current_response.data
                    
                    # Test mood analysis
                    mood_analysis = weather.analyze_atmospheric_mood(current_weather)
                    test_result['tests'].append({
                        'name': 'analyze_atmospheric_mood',
                        'status': 'passed',
                        'mood': mood_analysis.primary_mood
                    })
                    
            except Exception as e:
                test_result['errors'].append(f"Current weather test failed: {e}")
            
            # Test forecast
            try:
                forecast_response = await weather.get_weather_forecast(days=3)
                test_result['tests'].append({
                    'name': 'get_weather_forecast',
                    'status': 'passed' if forecast_response.success else 'failed'
                })
            except Exception as e:
                test_result['errors'].append(f"Weather forecast test failed: {e}")
            
            # Test comprehensive weather data
            try:
                comprehensive_data = await weather.get_comprehensive_weather_data()
                has_error = "error" in comprehensive_data
                test_result['tests'].append({
                    'name': 'get_comprehensive_data',
                    'status': 'failed' if has_error else 'passed'
                })
            except Exception as e:
                test_result['errors'].append(f"Comprehensive weather data test failed: {e}")
            
            # Determine overall status
            passed_tests = sum(1 for t in test_result['tests'] if t['status'] == 'passed')
            total_tests = len(test_result['tests'])
            
            if passed_tests == total_tests:
                test_result['status'] = 'passed'
            elif passed_tests > 0:
                test_result['status'] = 'partial'
            else:
                test_result['status'] = 'failed'
                
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f"Weather service test failed: {e}")
        
        self.test_results['weather'] = test_result
        logger.info(f"Weather service test completed: {test_result['status']}")
    
    async def _test_spotify_service(self):
        """Test Spotify API service (if configured)"""
        logger.info("Testing Spotify service...")
        
        test_result = {
            'status': 'unknown',
            'tests': [],
            'errors': []
        }
        
        try:
            spotify = self.services['spotify']
            
            # Test health check
            health_ok = await spotify.health_check()
            test_result['tests'].append({
                'name': 'health_check',
                'status': 'passed' if health_ok else 'failed'
            })
            
            if not health_ok:
                test_result['status'] = 'failed'
                test_result['errors'].append("Spotify health check failed")
            else:
                # Test currently playing
                current_response = await spotify.get_currently_playing()
                test_result['tests'].append({
                    'name': 'get_currently_playing',
                    'status': 'passed' if current_response.success else 'failed',
                    'is_playing': current_response.data.is_playing if current_response.data else False
                })
                
                # Test mood analysis
                mood_response = await spotify.analyze_current_mood()
                test_result['tests'].append({
                    'name': 'analyze_current_mood',
                    'status': 'passed' if mood_response.success else 'failed'
                })
                
                test_result['status'] = 'passed'
                
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f"Spotify service test failed: {e}")
        
        self.test_results['spotify'] = test_result
        logger.info(f"Spotify service test completed: {test_result['status']}")
    
    async def _test_wakatime_service(self):
        """Test WakaTime API service (if configured)"""
        logger.info("Testing WakaTime service...")
        
        test_result = {
            'status': 'unknown',
            'tests': [],
            'errors': []
        }
        
        try:
            wakatime = self.services['wakatime']
            
            # Test health check
            health_ok = await wakatime.health_check()
            test_result['tests'].append({
                'name': 'health_check',
                'status': 'passed' if health_ok else 'failed'
            })
            
            if health_ok:
                # Test productivity analysis
                productivity_response = await wakatime.get_productivity_analysis(7)
                test_result['tests'].append({
                    'name': 'get_productivity_analysis',
                    'status': 'passed' if productivity_response.success else 'failed'
                })
                
                test_result['status'] = 'passed'
            else:
                test_result['status'] = 'failed'
                
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f"WakaTime service test failed: {e}")
        
        self.test_results['wakatime'] = test_result
        logger.info(f"WakaTime service test completed: {test_result['status']}")
    
    async def _test_social_service(self):
        """Test Social Media API service (if configured)"""
        logger.info("Testing Social service...")
        
        test_result = {
            'status': 'unknown',
            'tests': [],
            'errors': []
        }
        
        try:
            social = self.services['social']
            
            # Test health check
            health_ok = await social.health_check()
            test_result['tests'].append({
                'name': 'health_check',
                'status': 'passed' if health_ok else 'failed'
            })
            
            if health_ok:
                # Test RSS feeds (always available)
                if social.rss_feeds:
                    rss_response = await social.get_rss_posts()
                    test_result['tests'].append({
                        'name': 'get_rss_posts',
                        'status': 'passed' if rss_response.success else 'failed',
                        'posts_count': len(rss_response.data) if rss_response.success else 0
                    })
                
                test_result['status'] = 'passed'
            else:
                test_result['status'] = 'failed'
                
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f"Social service test failed: {e}")
        
        self.test_results['social'] = test_result
        logger.info(f"Social service test completed: {test_result['status']}")
    
    async def _test_data_processors(self):
        """Test data processing engines"""
        logger.info("Testing data processors...")
        
        # Test Growth Engine
        await self._test_growth_engine()
        
        # Test Mood Engine
        await self._test_mood_engine()
        
        # Test Analytics Processor
        await self._test_analytics_processor()
    
    async def _test_growth_engine(self):
        """Test Growth Engine"""
        logger.info("Testing Growth Engine...")
        
        test_result = {
            'status': 'unknown',
            'tests': [],
            'errors': []
        }
        
        try:
            growth_engine = self.engines['growth']
            
            # Test portfolio overview
            portfolio = await growth_engine.get_portfolio_overview()
            has_error = "error" in portfolio
            test_result['tests'].append({
                'name': 'get_portfolio_overview',
                'status': 'failed' if has_error else 'passed',
                'projects_analyzed': portfolio.get('total_projects', 0)
            })
            
            test_result['status'] = 'failed' if has_error else 'passed'
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f"Growth engine test failed: {e}")
        
        self.test_results['growth_engine'] = test_result
        logger.info(f"Growth engine test completed: {test_result['status']}")
    
    async def _test_mood_engine(self):
        """Test Mood Engine"""
        logger.info("Testing Mood Engine...")
        
        test_result = {
            'status': 'unknown',
            'tests': [],
            'errors': []
        }
        
        try:
            mood_engine = self.engines['mood']
            
            # Test mood synthesis
            mood = await mood_engine.synthesize_current_mood()
            test_result['tests'].append({
                'name': 'synthesize_current_mood',
                'status': 'passed',
                'atmosphere': mood.primary_atmosphere.value,
                'confidence': mood.confidence
            })
            
            # Test mood trends
            trends = await mood_engine.get_mood_trends(24)
            has_error = "error" in trends
            test_result['tests'].append({
                'name': 'get_mood_trends',
                'status': 'failed' if has_error else 'passed'
            })
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f"Mood engine test failed: {e}")
        
        self.test_results['mood_engine'] = test_result
        logger.info(f"Mood engine test completed: {test_result['status']}")
    
    async def _test_analytics_processor(self):
        """Test Analytics Processor"""
        logger.info("Testing Analytics Processor...")
        
        test_result = {
            'status': 'unknown',
            'tests': [],
            'errors': []
        }
        
        try:
            analytics = self.engines['analytics']
            
            # Test visitor tracking
            visitor_id = "test_visitor_123"
            await analytics.track_interaction(
                raw_visitor_id=visitor_id,
                interaction_type="page_view",
                page_url="/test",
                user_agent="Test User Agent"
            )
            
            test_result['tests'].append({
                'name': 'track_interaction',
                'status': 'passed'
            })
            
            # Test engagement metrics
            metrics = analytics.get_engagement_metrics(24)
            test_result['tests'].append({
                'name': 'get_engagement_metrics',
                'status': 'passed',
                'unique_visitors': metrics.unique_visitors_24h
            })
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f"Analytics processor test failed: {e}")
        
        self.test_results['analytics_processor'] = test_result
        logger.info(f"Analytics processor test completed: {test_result['status']}")
    
    async def _test_infrastructure(self):
        """Test infrastructure components"""
        logger.info("Testing infrastructure...")
        
        # Test Cache Manager
        await self._test_cache_manager()
        
        # Test Rate Limiter
        await self._test_rate_limiter()
        
        # Test Privacy Manager
        await self._test_privacy_manager()
    
    async def _test_cache_manager(self):
        """Test Cache Manager"""
        logger.info("Testing Cache Manager...")
        
        test_result = {
            'status': 'unknown',
            'tests': [],
            'errors': []
        }
        
        try:
            cache = self.infrastructure['cache']
            
            # Test cache operations
            test_key = "integration_test_key"
            test_value = {"test": "data", "timestamp": datetime.utcnow().isoformat()}
            
            # Test set
            set_result = await cache.set(test_key, test_value, ttl_seconds=300)
            test_result['tests'].append({
                'name': 'cache_set',
                'status': 'passed' if set_result else 'failed'
            })
            
            # Test get
            get_result = await cache.get(test_key)
            test_result['tests'].append({
                'name': 'cache_get',
                'status': 'passed' if get_result == test_value else 'failed'
            })
            
            # Test stats
            stats = cache.get_comprehensive_stats()
            test_result['tests'].append({
                'name': 'get_stats',
                'status': 'passed',
                'hit_rate': stats.hit_rate
            })
            
            # Clean up
            await cache.delete(test_key)
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f"Cache manager test failed: {e}")
        
        self.test_results['cache_manager'] = test_result
        logger.info(f"Cache manager test completed: {test_result['status']}")
    
    async def _test_rate_limiter(self):
        """Test Rate Limiter"""
        logger.info("Testing Rate Limiter...")
        
        test_result = {
            'status': 'unknown',
            'tests': [],
            'errors': []
        }
        
        try:
            limiter = self.infrastructure['rate_limiter']
            
            # Test rate limit check
            service_name = "test_service"
            result, status = await limiter.check_rate_limit(service_name)
            
            test_result['tests'].append({
                'name': 'check_rate_limit',
                'status': 'passed',
                'result': result.value
            })
            
            # Test statistics
            stats = limiter.get_global_statistics()
            test_result['tests'].append({
                'name': 'get_statistics',
                'status': 'passed',
                'enabled': stats['enabled']
            })
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f"Rate limiter test failed: {e}")
        
        self.test_results['rate_limiter'] = test_result
        logger.info(f"Rate limiter test completed: {test_result['status']}")
    
    async def _test_privacy_manager(self):
        """Test Privacy Manager"""
        logger.info("Testing Privacy Manager...")
        
        test_result = {
            'status': 'unknown',
            'tests': [],
            'errors': []
        }
        
        try:
            privacy = self.infrastructure['privacy']
            
            # Test visitor ID generation
            visitor_id = privacy.generate_visitor_id("127.0.0.1", "Test User Agent")
            test_result['tests'].append({
                'name': 'generate_visitor_id',
                'status': 'passed',
                'visitor_id_length': len(visitor_id)
            })
            
            # Test IP anonymization
            anon_ip = privacy.anonymize_ip_address("192.168.1.1")
            test_result['tests'].append({
                'name': 'anonymize_ip_address',
                'status': 'passed',
                'anonymized': len(anon_ip) == 16
            })
            
            # Test dashboard data
            dashboard = privacy.get_privacy_dashboard_data()
            test_result['tests'].append({
                'name': 'get_privacy_dashboard_data',
                'status': 'passed',
                'consent_required': dashboard['consent_summary']['consent_required']
            })
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f"Privacy manager test failed: {e}")
        
        self.test_results['privacy_manager'] = test_result
        logger.info(f"Privacy manager test completed: {test_result['status']}")
    
    async def _test_real_time_pipeline(self):
        """Test real-time pipeline components"""
        logger.info("Testing real-time pipeline...")
        
        # Test WebSocket Manager
        await self._test_websocket_manager()
        
        # Test Task Scheduler
        await self._test_task_scheduler()
    
    async def _test_websocket_manager(self):
        """Test WebSocket Manager"""
        logger.info("Testing WebSocket Manager...")
        
        test_result = {
            'status': 'unknown',
            'tests': [],
            'errors': []
        }
        
        try:
            ws_manager = self.infrastructure['websocket']
            
            # Test connection stats
            stats = ws_manager.get_connection_stats()
            test_result['tests'].append({
                'name': 'get_connection_stats',
                'status': 'passed',
                'total_connections': stats['total_connections']
            })
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f"WebSocket manager test failed: {e}")
        
        self.test_results['websocket_manager'] = test_result
        logger.info(f"WebSocket manager test completed: {test_result['status']}")
    
    async def _test_task_scheduler(self):
        """Test Task Scheduler"""
        logger.info("Testing Task Scheduler...")
        
        test_result = {
            'status': 'unknown',
            'tests': [],
            'errors': []
        }
        
        try:
            scheduler = self.infrastructure['scheduler']
            
            # Test scheduler stats
            stats = scheduler.get_scheduler_stats()
            test_result['tests'].append({
                'name': 'get_scheduler_stats',
                'status': 'passed',
                'registered_tasks': stats['registered_tasks']
            })
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f"Task scheduler test failed: {e}")
        
        self.test_results['task_scheduler'] = test_result
        logger.info(f"Task scheduler test completed: {test_result['status']}")
    
    def _generate_summary_report(self):
        """Generate comprehensive test summary report"""
        
        total_services = len(self.test_results)
        passed_services = sum(1 for result in self.test_results.values() 
                            if result.get('status') == 'passed')
        failed_services = sum(1 for result in self.test_results.values() 
                            if result.get('status') == 'failed')
        skipped_services = sum(1 for result in self.test_results.values() 
                             if result.get('status') == 'skipped')
        
        summary = {
            'overall_status': 'passed' if failed_services == 0 else 'partial' if passed_services > 0 else 'failed',
            'total_services_tested': total_services,
            'services_passed': passed_services,
            'services_failed': failed_services,
            'services_skipped': skipped_services,
            'test_timestamp': datetime.utcnow().isoformat(),
            'environment': {
                'github_configured': integration_settings.github.is_configured,
                'spotify_configured': integration_settings.spotify.is_configured,
                'weather_configured': integration_settings.weather.is_configured,
                'wakatime_configured': integration_settings.wakatime.is_configured,
                'social_configured': integration_settings.social.is_configured,
            }
        }
        
        self.test_results['_summary'] = summary
        
        logger.info(f"Test Summary: {passed_services}/{total_services} services passed")
        logger.info(f"Overall Status: {summary['overall_status']}")


async def run_integration_tests():
    """Run the complete integration test suite"""
    tester = IntegrationTester()
    results = await tester.run_all_tests()
    
    # Print summary
    summary = results.get('_summary', {})
    print("\n" + "="*80)
    print("DIGITAL GREENHOUSE INTEGRATION TEST RESULTS")
    print("="*80)
    print(f"Overall Status: {summary.get('overall_status', 'unknown').upper()}")
    print(f"Services Passed: {summary.get('services_passed', 0)}")
    print(f"Services Failed: {summary.get('services_failed', 0)}")
    print(f"Services Skipped: {summary.get('services_skipped', 0)}")
    print(f"Test Timestamp: {summary.get('test_timestamp', 'unknown')}")
    print("\nDetailed Results:")
    print("-"*40)
    
    for service_name, result in results.items():
        if service_name == '_summary':
            continue
        
        status = result.get('status', 'unknown')
        status_symbol = {
            'passed': '✓',
            'failed': '✗',
            'partial': '⚠',
            'skipped': '⊝'
        }.get(status, '?')
        
        print(f"{status_symbol} {service_name.ljust(20)} {status.upper()}")
        
        if result.get('errors'):
            for error in result['errors']:
                print(f"    Error: {error}")
    
    print("="*80)
    
    return results


if __name__ == "__main__":
    asyncio.run(run_integration_tests())