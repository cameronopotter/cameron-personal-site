/**
 * K6 Load Testing Suite for Digital Greenhouse
 * Advanced performance testing with detailed metrics and scenarios
 */

import http from 'k6/http';
import ws from 'k6/ws';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import { SharedArray } from 'k6/data';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const WS_URL = __ENV.WS_URL || 'ws://localhost:8000';
const FRONTEND_URL = __ENV.FRONTEND_URL || 'http://localhost:3000';

// Custom metrics
const apiResponseTime = new Trend('api_response_time');
const wsConnectionTime = new Trend('websocket_connection_time');
const errorRate = new Rate('error_rate');
const activeConnections = new Gauge('active_websocket_connections');
const throughput = new Counter('requests_per_second');

// Test data
const testData = new SharedArray('test_data', function () {
  const searchTerms = ['react', 'python', 'javascript', 'api', 'frontend', 'backend', 'database'];
  const skillCategories = ['frontend', 'backend', 'database', 'devops', 'mobile'];
  const userAgents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'
  ];
  
  return {
    searchTerms,
    skillCategories,
    userAgents,
    generateUserId: () => Math.random().toString(36).substr(2, 9)
  };
});

// Test scenarios configuration
export const options = {
  scenarios: {
    // Baseline load test
    baseline_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 20 },   // Ramp up to 20 users over 2 minutes
        { duration: '5m', target: 20 },   // Stay at 20 users for 5 minutes
        { duration: '2m', target: 40 },   // Ramp up to 40 users over 2 minutes
        { duration: '5m', target: 40 },   // Stay at 40 users for 5 minutes
        { duration: '2m', target: 0 },    // Ramp down to 0 users over 2 minutes
      ],
      gracefulRampDown: '30s',
    },
    
    // Stress test
    stress_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 100 },  // Ramp up to 100 users
        { duration: '5m', target: 100 },  // Stay at 100 users
        { duration: '2m', target: 200 },  // Ramp up to 200 users
        { duration: '5m', target: 200 },  // Stay at 200 users
        { duration: '2m', target: 0 },    // Ramp down
      ],
      gracefulRampDown: '30s',
      env: { TEST_TYPE: 'stress' },
    },
    
    // Spike test
    spike_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 20 },   // Normal load
        { duration: '30s', target: 500 }, // Sudden spike
        { duration: '1m', target: 500 },  // Maintain spike
        { duration: '30s', target: 20 },  // Back to normal
        { duration: '2m', target: 20 },   // Stay normal
        { duration: '1m', target: 0 },    // Ramp down
      ],
      gracefulRampDown: '30s',
      env: { TEST_TYPE: 'spike' },
    },
    
    // WebSocket test
    websocket_test: {
      executor: 'constant-vus',
      vus: 50,
      duration: '10m',
      exec: 'websocketTest',
      env: { TEST_TYPE: 'websocket' },
    },
    
    // Mobile user simulation
    mobile_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '3m', target: 30 },
        { duration: '10m', target: 30 },
        { duration: '2m', target: 0 },
      ],
      exec: 'mobileUserTest',
      env: { TEST_TYPE: 'mobile' },
    },
  },
  
  // Thresholds for performance requirements
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% under 500ms, 99% under 1s
    http_req_failed: ['rate<0.01'],                  // Less than 1% errors
    api_response_time: ['avg<300', 'p(95)<600'],     // Average under 300ms, 95% under 600ms
    websocket_connection_time: ['avg<1000'],         // WebSocket connections under 1s
    error_rate: ['rate<0.02'],                       // Less than 2% errors
  },
  
  // Global settings
  userAgent: 'K6-LoadTest-DigitalGreenhouse/1.0',
  insecureSkipTLSVerify: true,
  noConnectionReuse: false,
};

/**
 * Default test scenario - simulates normal user behavior
 */
export default function () {
  const userId = testData.generateUserId();
  
  group('Garden Browsing Flow', function () {
    // 1. Load main garden data (most common operation)
    let response = http.get(`${BASE_URL}/api/v1/garden/data`, {
      headers: {
        'Accept': 'application/json',
        'User-Agent': getRandomUserAgent(),
      },
      tags: { name: 'load_garden_data' },
    });
    
    check(response, {
      'garden data loaded': (r) => r.status === 200,
      'response time < 500ms': (r) => r.timings.duration < 500,
      'has projects': (r) => JSON.parse(r.body).projects.length > 0,
    });
    
    apiResponseTime.add(response.timings.duration);
    throughput.add(1);
    
    if (response.status !== 200) {
      errorRate.add(1);
    } else {
      errorRate.add(0);
    }
    
    sleep(Math.random() * 2 + 1); // 1-3 seconds thinking time
    
    // 2. Browse projects
    response = http.get(`${BASE_URL}/api/v1/projects/`, {
      tags: { name: 'list_projects' },
    });
    
    check(response, {
      'projects loaded': (r) => r.status === 200,
    });
    
    if (response.status === 200) {
      const projects = JSON.parse(response.body);
      if (projects.length > 0) {
        // View a random project
        const randomProject = projects[Math.floor(Math.random() * Math.min(5, projects.length))];
        
        response = http.get(`${BASE_URL}/api/v1/projects/${randomProject.id}`, {
          tags: { name: 'view_project_details' },
        });
        
        check(response, {
          'project details loaded': (r) => r.status === 200,
        });
      }
    }
    
    sleep(Math.random() * 1.5 + 0.5); // 0.5-2 seconds
    
    // 3. Explore skills (less frequent)
    if (Math.random() > 0.3) { // 70% of users explore skills
      response = http.get(`${BASE_URL}/api/v1/skills/`, {
        tags: { name: 'list_skills' },
      });
      
      check(response, {
        'skills loaded': (r) => r.status === 200,
      });
    }
    
    // 4. Search functionality (occasional use)
    if (Math.random() > 0.7) { // 30% of users search
      const searchTerm = testData.searchTerms[Math.floor(Math.random() * testData.searchTerms.length)];
      
      response = http.get(`${BASE_URL}/api/v1/garden/search?query=${searchTerm}&limit=10`, {
        tags: { name: 'search_garden' },
      });
      
      check(response, {
        'search completed': (r) => r.status === 200,
        'search results returned': (r) => r.status === 200 && JSON.parse(r.body).results !== undefined,
      });
    }
    
    // 5. Check weather (background request)
    if (Math.random() > 0.5) { // 50% chance
      response = http.get(`${BASE_URL}/api/v1/weather/current`, {
        tags: { name: 'check_weather' },
      });
      
      check(response, {
        'weather data loaded': (r) => r.status === 200,
      });
    }
    
    sleep(Math.random() * 3 + 1); // 1-4 seconds before next iteration
  });
}

/**
 * WebSocket-specific test
 */
export function websocketTest() {
  const userId = testData.generateUserId();
  const startTime = Date.now();
  
  const response = ws.connect(`${WS_URL}/ws/garden/${userId}`, {
    headers: {
      'User-Agent': getRandomUserAgent(),
    },
  }, function (socket) {
    wsConnectionTime.add(Date.now() - startTime);
    activeConnections.add(1);
    
    socket.on('open', function () {
      console.log(`WebSocket connection established for user ${userId}`);
      
      // Send initial message
      socket.send(JSON.stringify({
        type: 'user_connected',
        user_id: userId,
        timestamp: new Date().toISOString(),
      }));
    });
    
    socket.on('message', function (message) {
      try {
        const data = JSON.parse(message);
        
        // Simulate processing different message types
        switch (data.type) {
          case 'garden_update':
            // Simulate handling garden updates
            break;
          case 'project_created':
            // Simulate handling project creation
            break;
          case 'skill_updated':
            // Simulate handling skill updates
            break;
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    });
    
    socket.on('error', function (e) {
      console.error('WebSocket error:', e);
      errorRate.add(1);
    });
    
    socket.on('close', function () {
      console.log(`WebSocket connection closed for user ${userId}`);
      activeConnections.add(-1);
    });
    
    // Periodically send messages
    const messageInterval = setInterval(function () {
      if (socket.readyState === 1) { // OPEN
        socket.send(JSON.stringify({
          type: 'ping',
          user_id: userId,
          timestamp: new Date().toISOString(),
        }));
      }
    }, 10000); // Every 10 seconds
    
    // Simulate user activity for 5-15 minutes
    const connectionDuration = Math.random() * 600000 + 300000; // 5-15 minutes
    
    setTimeout(function () {
      clearInterval(messageInterval);
      socket.close();
    }, connectionDuration);
    
    // Make some HTTP requests while WebSocket is connected
    sleep(Math.random() * 5 + 2);
    
    for (let i = 0; i < 3; i++) {
      const response = http.get(`${BASE_URL}/api/v1/garden/data`, {
        tags: { name: 'garden_data_with_ws' },
      });
      
      check(response, {
        'API works with WebSocket': (r) => r.status === 200,
      });
      
      sleep(Math.random() * 10 + 5); // 5-15 seconds between requests
    }
  });
  
  check(response, {
    'WebSocket connection established': (r) => r && r.status === 101,
  });
}

/**
 * Mobile user test with different patterns
 */
export function mobileUserTest() {
  const userId = testData.generateUserId();
  const mobileUserAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15';
  
  group('Mobile User Flow', function () {
    // Mobile users typically have slower connections and interactions
    
    // 1. Load garden data with mobile optimizations
    let response = http.get(`${BASE_URL}/api/v1/garden/data?mobile=true&limit=5`, {
      headers: {
        'Accept': 'application/json',
        'User-Agent': mobileUserAgent,
        'Accept-Encoding': 'gzip, deflate',
      },
      tags: { name: 'mobile_garden_data' },
    });
    
    check(response, {
      'mobile garden data loaded': (r) => r.status === 200,
      'response time suitable for mobile': (r) => r.timings.duration < 1000,
    });
    
    // Longer thinking time for mobile users
    sleep(Math.random() * 4 + 2); // 2-6 seconds
    
    // 2. Touch-based project selection (fewer projects viewed)
    response = http.get(`${BASE_URL}/api/v1/projects/?limit=3`, {
      headers: { 'User-Agent': mobileUserAgent },
      tags: { name: 'mobile_projects' },
    });
    
    if (response.status === 200) {
      const projects = JSON.parse(response.body);
      if (projects.length > 0) {
        const project = projects[0]; // Mobile users often select first item
        
        response = http.get(`${BASE_URL}/api/v1/projects/${project.id}`, {
          headers: { 'User-Agent': mobileUserAgent },
          tags: { name: 'mobile_project_detail' },
        });
        
        check(response, {
          'mobile project detail loaded': (r) => r.status === 200,
        });
      }
    }
    
    sleep(Math.random() * 3 + 1.5); // 1.5-4.5 seconds
    
    // 3. Simple search (mobile users use simpler queries)
    if (Math.random() > 0.8) { // Only 20% of mobile users search
      const simpleSearchTerms = ['react', 'python', 'js'];
      const term = simpleSearchTerms[Math.floor(Math.random() * simpleSearchTerms.length)];
      
      response = http.get(`${BASE_URL}/api/v1/garden/search?query=${term}&limit=5`, {
        headers: { 'User-Agent': mobileUserAgent },
        tags: { name: 'mobile_search' },
      });
      
      check(response, {
        'mobile search completed': (r) => r.status === 200,
      });
    }
  });
}

/**
 * Stress test specific operations
 */
export function stressTest() {
  const operations = [
    () => {
      // Heavy aggregation query
      const response = http.get(`${BASE_URL}/api/v1/analytics/summary`, {
        tags: { name: 'heavy_analytics' },
      });
      check(response, { 'analytics under stress': (r) => r.status === 200 });
    },
    () => {
      // Complex search
      const response = http.get(`${BASE_URL}/api/v1/garden/search?query=python%20javascript&category=backend&sort=popularity&limit=50`, {
        tags: { name: 'complex_search' },
      });
      check(response, { 'complex search under stress': (r) => r.status === 200 });
    },
    () => {
      // Export operation (expensive)
      const response = http.get(`${BASE_URL}/api/v1/garden/export?format=json`, {
        tags: { name: 'export_stress' },
      });
      check(response, { 'export under stress': (r) => r.status === 200 });
    },
  ];
  
  // Execute random operation
  const operation = operations[Math.floor(Math.random() * operations.length)];
  operation();
  
  sleep(0.1); // Minimal sleep for stress test
}

/**
 * Helper functions
 */
function getRandomUserAgent() {
  return testData.userAgents[Math.floor(Math.random() * testData.userAgents.length)];
}

/**
 * Custom summary function for detailed reporting
 */
export function handleSummary(data) {
  return {
    'load-test-report.html': htmlReport(data),
    'load-test-summary.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

/**
 * Setup function - runs once before the test
 */
export function setup() {
  console.log('🚀 Starting Digital Greenhouse Load Tests...');
  console.log(`📊 Target: ${BASE_URL}`);
  console.log(`🔌 WebSocket: ${WS_URL}`);
  
  // Verify API is accessible
  const response = http.get(`${BASE_URL}/health`);
  if (response.status !== 200) {
    throw new Error(`API health check failed: ${response.status}`);
  }
  
  console.log('✅ API health check passed');
  
  return {
    startTime: new Date(),
    baseUrl: BASE_URL,
  };
}

/**
 * Teardown function - runs once after the test
 */
export function teardown(data) {
  console.log('🏁 Load test completed');
  console.log(`📈 Test duration: ${new Date() - data.startTime}ms`);
  
  // Could send results to monitoring system here
}