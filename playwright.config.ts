import { defineConfig, devices } from '@playwright/test';

/**
 * Digital Greenhouse Playwright Configuration
 * Comprehensive E2E testing setup with performance, accessibility, and visual testing
 */
export default defineConfig({
  testDir: './e2e',
  
  /* Run tests in files in parallel */
  fullyParallel: true,
  
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  
  /* Reporter to use. */
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/results.xml' }],
    ['line'],
    ...(process.env.CI ? [['github']] : [])
  ],
  
  /* Shared settings for all the projects below. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    
    /* Collect trace when retrying the failed test. */
    trace: 'on-first-retry',
    
    /* Take screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Record video on failure */
    video: 'retain-on-failure',
    
    /* Global test timeout */
    actionTimeout: 30000,
    navigationTimeout: 30000,
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    /* Mobile testing */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },

    /* High-DPI display testing */
    {
      name: 'Desktop Chrome HiDPI',
      use: {
        ...devices['Desktop Chrome HiDPI'],
      },
    },

    /* Accessibility testing project */
    {
      name: 'accessibility',
      testMatch: '**/*.accessibility.spec.ts',
      use: { ...devices['Desktop Chrome'] },
    },

    /* Performance testing project */
    {
      name: 'performance',
      testMatch: '**/*.performance.spec.ts',
      use: { 
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: ['--disable-web-security', '--disable-dev-shm-usage', '--no-sandbox']
        }
      },
    },

    /* Visual regression testing */
    {
      name: 'visual',
      testMatch: '**/*.visual.spec.ts',
      use: { 
        ...devices['Desktop Chrome'],
        // Ensure consistent screenshots
        viewport: { width: 1280, height: 720 }
      },
    },
  ],

  /* Test match patterns */
  testMatch: [
    'e2e/**/*.{test,spec}.{js,ts,jsx,tsx}',
    'e2e/**/*.{accessibility,performance,visual}.spec.{js,ts,jsx,tsx}'
  ],

  /* Test ignore patterns */
  testIgnore: [
    '**/node_modules/**',
    '**/dist/**',
    '**/.git/**'
  ],

  /* Global setup and teardown */
  globalSetup: require.resolve('./e2e/global-setup.ts'),
  globalTeardown: require.resolve('./e2e/global-teardown.ts'),

  /* Folder for test artifacts such as screenshots, videos, traces, etc. */
  outputDir: 'test-results/',

  /* Run your local dev server before starting the tests */
  webServer: [
    {
      command: 'npm run dev',
      port: 3000,
      reuseExistingServer: !process.env.CI,
      cwd: './frontend',
      timeout: 120000,
    },
    {
      command: 'python -m uvicorn app.main:app --reload --port 8000',
      port: 8000,
      reuseExistingServer: !process.env.CI,
      cwd: './backend',
      timeout: 120000,
    }
  ],

  /* Test timeout */
  timeout: 60000,
  expect: {
    /* Timeout for assertions */
    timeout: 10000,
    /* Threshold for visual comparisons */
    threshold: 0.2,
    /* Animation handling */
    toMatchSnapshot: {
      mode: 'css',
      animations: 'disabled',
    },
  },

  /* Maximum failures before stopping */
  maxFailures: process.env.CI ? 10 : undefined,
});