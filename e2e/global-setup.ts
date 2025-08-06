import { chromium, FullConfig } from '@playwright/test';

/**
 * Global setup for Playwright tests.
 * This runs once before all tests and sets up the testing environment.
 */
async function globalSetup(config: FullConfig) {
  console.log('🌱 Starting Digital Greenhouse E2E Test Setup...');
  
  // Launch browser for setup tasks
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Wait for both frontend and backend to be ready
    console.log('⏳ Waiting for frontend to be ready...');
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    console.log('⏳ Waiting for backend to be ready...');
    await page.goto('http://localhost:8000/health');
    await page.waitForResponse(response => response.status() === 200);
    
    // Setup test data if needed
    console.log('📊 Setting up test data...');
    await setupTestData(page);
    
    // Warm up the application
    console.log('🔥 Warming up the application...');
    await warmupApplication(page);
    
    console.log('✅ E2E Test Setup Complete!');
    
  } catch (error) {
    console.error('❌ E2E Test Setup Failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

/**
 * Setup test data for consistent testing
 */
async function setupTestData(page: any) {
  try {
    // Create test projects
    const testProjects = [
      {
        name: 'E2E Test Project 1',
        description: 'First test project for E2E testing',
        github_url: 'https://github.com/test/project1',
        technologies: ['React', 'TypeScript', 'Three.js'],
        status: 'active'
      },
      {
        name: 'E2E Test Project 2', 
        description: 'Second test project for E2E testing',
        github_url: 'https://github.com/test/project2',
        technologies: ['Python', 'FastAPI', 'PostgreSQL'],
        status: 'completed'
      }
    ];
    
    for (const project of testProjects) {
      await page.request.post('http://localhost:8000/api/v1/projects/', {
        data: project,
        headers: {
          'Content-Type': 'application/json'
        }
      });
    }
    
    // Create test skills
    const testSkills = [
      {
        name: 'React',
        category: 'frontend',
        level: 95,
        years_experience: 5
      },
      {
        name: 'Python',
        category: 'backend',
        level: 90,
        years_experience: 6
      },
      {
        name: 'Three.js',
        category: 'frontend',
        level: 85,
        years_experience: 3
      }
    ];
    
    for (const skill of testSkills) {
      await page.request.post('http://localhost:8000/api/v1/skills/', {
        data: skill,
        headers: {
          'Content-Type': 'application/json'
        }
      });
    }
    
    console.log('✅ Test data created successfully');
    
  } catch (error) {
    console.warn('⚠️  Could not create test data:', error);
    // Don't fail setup if test data creation fails
  }
}

/**
 * Warm up the application by visiting key pages
 */
async function warmupApplication(page: any) {
  try {
    const warmupPages = [
      'http://localhost:3000/',
      'http://localhost:3000/projects',
      'http://localhost:3000/skills',
      'http://localhost:8000/api/v1/garden/data',
      'http://localhost:8000/api/v1/projects/',
      'http://localhost:8000/api/v1/skills/'
    ];
    
    for (const url of warmupPages) {
      await page.goto(url);
      await page.waitForLoadState('networkidle');
      
      // Small delay to ensure proper loading
      await page.waitForTimeout(500);
    }
    
    console.log('✅ Application warmed up successfully');
    
  } catch (error) {
    console.warn('⚠️  Application warmup had issues:', error);
    // Don't fail setup if warmup has issues
  }
}

export default globalSetup;