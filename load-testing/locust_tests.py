#!/usr/bin/env python3
"""
Load testing suite for Digital Greenhouse using Locust
Comprehensive testing of API endpoints, WebSocket connections, and user scenarios
"""

import json
import random
import time
from typing import Dict, List, Any, Optional
import uuid
import asyncio
import websockets
from urllib.parse import urljoin

from locust import HttpUser, task, between, events
from locust.contrib.fasthttp import FastHttpUser
import gevent
from gevent import socket

# Test configuration
API_BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"
FRONTEND_BASE_URL = "http://localhost:3000"

class DigitalGardenUser(FastHttpUser):
    """
    Simulates a typical user browsing the Digital Greenhouse
    """
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    weight = 3  # Higher weight = more common user type
    
    def on_start(self):
        """Initialize user session"""
        self.user_id = str(uuid.uuid4())
        self.session_data = {
            'projects_viewed': [],
            'skills_explored': [],
            'interactions': 0
        }
        
        # Login or create session if needed
        self.setup_session()
    
    def setup_session(self):
        """Setup user session with the backend"""
        response = self.client.post("/api/v1/visitors/", json={
            "user_id": self.user_id,
            "user_agent": "Load-Test-User",
            "ip_address": f"192.168.1.{random.randint(1, 254)}"
        })
        
        if response.status_code not in [200, 201]:
            print(f"Failed to setup session: {response.status_code}")

    @task(10)  # Weight 10 - very common
    def browse_garden_data(self):
        """Load the main garden data - most common operation"""
        with self.client.get("/api/v1/garden/data", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.session_data['projects_viewed'].extend([p['id'] for p in data.get('projects', [])[:3]])
                response.success()
            else:
                response.failure(f"Failed to load garden data: {response.status_code}")

    @task(8)  # Weight 8 - common
    def view_projects(self):
        """Browse through projects"""
        response = self.client.get("/api/v1/projects/")
        if response.status_code == 200:
            projects = response.json()
            if projects:
                # View a random project
                project = random.choice(projects[:5])  # Top 5 projects
                self.client.get(f"/api/v1/projects/{project['id']}")
                self.session_data['projects_viewed'].append(project['id'])

    @task(6)  # Weight 6 - moderately common
    def explore_skills(self):
        """Explore skills data"""
        response = self.client.get("/api/v1/skills/")
        if response.status_code == 200:
            skills = response.json()
            if skills:
                # Explore skills by category
                skill = random.choice(skills[:3])
                self.client.get(f"/api/v1/skills/{skill['id']}")
                self.session_data['skills_explored'].append(skill['id'])

    @task(4)  # Weight 4 - less common
    def check_weather(self):
        """Check weather data for the garden"""
        self.client.get("/api/v1/weather/current")

    @task(3)  # Weight 3 - less common
    def view_analytics(self):
        """View garden analytics"""
        self.client.get("/api/v1/analytics/summary")

    @task(2)  # Weight 2 - uncommon
    def search_garden(self):
        """Search through garden content"""
        search_terms = ['react', 'python', 'javascript', 'api', 'frontend', 'backend']
        query = random.choice(search_terms)
        
        self.client.get(f"/api/v1/garden/search?query={query}&limit=10")

    @task(1)  # Weight 1 - rare
    def export_data(self):
        """Export garden data - expensive operation"""
        self.client.get("/api/v1/garden/export?format=json", name="export_garden_data")

    def on_stop(self):
        """Cleanup when user stops"""
        # Record session end
        try:
            self.client.patch(f"/api/v1/visitors/{self.user_id}", json={
                "session_ended": True,
                "interactions": self.session_data['interactions'],
                "pages_viewed": len(set(self.session_data['projects_viewed'] + 
                                       self.session_data['skills_explored']))
            })
        except:
            pass  # Ignore cleanup errors

class IntensiveAPIUser(FastHttpUser):
    """
    Power user that makes intensive API calls
    Tests system under heavy API load
    """
    
    wait_time = between(0.1, 0.5)  # Very fast requests
    weight = 1  # Lower weight - fewer of these users
    
    def on_start(self):
        self.user_id = str(uuid.uuid4())
    
    @task(5)
    def rapid_fire_requests(self):
        """Make rapid API calls"""
        endpoints = [
            "/api/v1/garden/data",
            "/api/v1/projects/",
            "/api/v1/skills/",
            "/api/v1/weather/current",
            "/api/v1/garden/health"
        ]
        
        # Make multiple requests rapidly
        for _ in range(3):
            endpoint = random.choice(endpoints)
            self.client.get(endpoint)
    
    @task(3)
    def concurrent_project_views(self):
        """View multiple projects concurrently"""
        # Get project list
        response = self.client.get("/api/v1/projects/")
        if response.status_code == 200:
            projects = response.json()[:10]  # Top 10 projects
            
            # View multiple projects quickly
            for project in random.sample(projects, min(5, len(projects))):
                self.client.get(f"/api/v1/projects/{project['id']}")
    
    @task(2)
    def stress_search(self):
        """Perform intensive search operations"""
        queries = [
            'a', 'e', 'i', 'react', 'python', 'javascript',
            'web development', 'api design', 'database'
        ]
        
        for query in random.sample(queries, 3):
            self.client.get(f"/api/v1/garden/search?query={query}&limit=50")

class WebSocketUser(HttpUser):
    """
    User that maintains WebSocket connections
    Tests real-time features and WebSocket scalability
    """
    
    wait_time = between(2, 10)
    weight = 2
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws_url = WS_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://')
        self.websocket = None
        self.user_id = str(uuid.uuid4())
    
    def on_start(self):
        """Establish WebSocket connection"""
        self.connect_websocket()
    
    def connect_websocket(self):
        """Connect to WebSocket endpoint"""
        try:
            import websocket
            
            def on_message(ws, message):
                self.handle_websocket_message(message)
            
            def on_error(ws, error):
                print(f"WebSocket error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                print("WebSocket connection closed")
            
            self.websocket = websocket.WebSocketApp(
                f"{self.ws_url}/ws/garden/{self.user_id}",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run WebSocket in background
            gevent.spawn(self.websocket.run_forever)
            
            # Give connection time to establish
            gevent.sleep(0.5)
            
        except Exception as e:
            print(f"Failed to connect WebSocket: {e}")
    
    def handle_websocket_message(self, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            # Process message types
            if data.get('type') == 'garden_update':
                pass  # Handle garden updates
            elif data.get('type') == 'project_created':
                pass  # Handle project creation
        except json.JSONDecodeError:
            pass
    
    @task(1)
    def send_websocket_message(self):
        """Send message via WebSocket"""
        if self.websocket:
            message = {
                "type": "ping",
                "user_id": self.user_id,
                "timestamp": time.time()
            }
            try:
                self.websocket.send(json.dumps(message))
            except Exception as e:
                print(f"Failed to send WebSocket message: {e}")
                self.connect_websocket()  # Reconnect if needed
    
    @task(3)
    def http_requests_with_websocket(self):
        """Make HTTP requests while maintaining WebSocket connection"""
        # Simulate user browsing while connected to WebSocket
        response = self.client.get("/api/v1/garden/data")
        if response.status_code == 200:
            # Simulate processing time
            gevent.sleep(random.uniform(0.1, 0.5))
    
    def on_stop(self):
        """Cleanup WebSocket connection"""
        if self.websocket:
            self.websocket.close()

class MobileUser(FastHttpUser):
    """
    Simulates mobile users with slower connections and different usage patterns
    """
    
    wait_time = between(2, 8)  # Slower interaction pace
    weight = 2
    
    def on_start(self):
        """Setup mobile user session"""
        self.user_id = str(uuid.uuid4())
        
        # Set mobile user agent
        self.client.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'
        })
    
    @task(8)
    def mobile_garden_view(self):
        """Optimized garden view for mobile"""
        # Request with mobile optimizations
        response = self.client.get("/api/v1/garden/data?mobile=true&limit=10")
        
        # Simulate slower processing on mobile
        gevent.sleep(random.uniform(0.5, 1.5))
    
    @task(5)
    def touch_interactions(self):
        """Simulate touch-based interactions"""
        # Simulate project selection via touch
        response = self.client.get("/api/v1/projects/?limit=5")  # Fewer items for mobile
        if response.status_code == 200:
            projects = response.json()
            if projects:
                project = random.choice(projects)
                self.client.get(f"/api/v1/projects/{project['id']}")
    
    @task(3)
    def mobile_optimized_requests(self):
        """Mobile-optimized API requests"""
        # Request compressed/optimized data
        self.client.headers.update({'Accept-Encoding': 'gzip, deflate'})
        
        endpoints = [
            "/api/v1/skills/?mobile=true",
            "/api/v1/weather/current?simplified=true",
            "/api/v1/garden/stats?mobile=true"
        ]
        
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)

# Custom event handlers for detailed metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Custom request event handler for detailed metrics"""
    if exception:
        print(f"Request failed: {name} - {exception}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Test start event handler"""
    print("🚀 Digital Greenhouse Load Test Starting...")
    print(f"Target: {API_BASE_URL}")
    print(f"WebSocket: {WS_BASE_URL}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Test stop event handler"""
    print("🏁 Digital Greenhouse Load Test Completed")
    
    # Print summary statistics
    stats = environment.stats
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Failed requests: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Max response time: {stats.total.max_response_time:.2f}ms")
    
    # Performance analysis
    if stats.total.avg_response_time > 500:
        print("⚠️  Warning: High average response time detected")
    
    if stats.total.num_failures > stats.total.num_requests * 0.01:
        print("⚠️  Warning: High failure rate detected")

# Additional test scenarios
class DatabaseStressUser(FastHttpUser):
    """
    Specifically stress test database operations
    """
    
    wait_time = between(0.1, 1)
    weight = 1
    
    @task(4)
    def complex_queries(self):
        """Perform complex database queries"""
        # Search with complex parameters
        self.client.get("/api/v1/garden/search?query=python&category=backend&sort=popularity&limit=50")
    
    @task(3)
    def aggregation_queries(self):
        """Test aggregation endpoints"""
        self.client.get("/api/v1/analytics/summary")
        self.client.get("/api/v1/garden/stats")
    
    @task(2)
    def concurrent_writes(self):
        """Simulate concurrent write operations (if applicable)"""
        # This would test write operations if your API supports them
        visitor_data = {
            "user_id": str(uuid.uuid4()),
            "ip_address": f"10.0.0.{random.randint(1, 254)}",
            "user_agent": "Load-Test-DB-User"
        }
        self.client.post("/api/v1/visitors/", json=visitor_data)

# Load testing profiles
class LightLoadProfile:
    """Light load profile for basic testing"""
    users = 50
    spawn_rate = 5
    duration = "5m"

class MediumLoadProfile:
    """Medium load profile for realistic testing"""
    users = 200
    spawn_rate = 10
    duration = "10m"

class HeavyLoadProfile:
    """Heavy load profile for stress testing"""
    users = 500
    spawn_rate = 25
    duration = "15m"

class SpikeTestProfile:
    """Spike test profile"""
    users = 1000
    spawn_rate = 100
    duration = "2m"

if __name__ == "__main__":
    print("""
    Digital Greenhouse Load Testing Suite
    
    Available User Types:
    - DigitalGardenUser: Normal browsing behavior (weight: 3)
    - IntensiveAPIUser: Heavy API usage (weight: 1)
    - WebSocketUser: Real-time connections (weight: 2)
    - MobileUser: Mobile device simulation (weight: 2)
    - DatabaseStressUser: Database stress testing (weight: 1)
    
    Load Profiles:
    - Light: 50 users, 5/s spawn rate, 5 minutes
    - Medium: 200 users, 10/s spawn rate, 10 minutes
    - Heavy: 500 users, 25/s spawn rate, 15 minutes
    - Spike: 1000 users, 100/s spawn rate, 2 minutes
    
    To run:
    locust -f load-testing/locust_tests.py --host=http://localhost:8000 --users=200 --spawn-rate=10 --run-time=10m
    
    For web UI:
    locust -f load-testing/locust_tests.py --host=http://localhost:8000
    """)