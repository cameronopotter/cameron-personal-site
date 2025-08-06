import { test, expect, Page } from '@playwright/test';

/**
 * Visual regression tests for Digital Greenhouse
 * Ensures UI consistency across changes and different environments
 * @visual
 */
test.describe('Digital Greenhouse - Visual Regression Tests', () => {
  
  // Configure viewport sizes for testing
  const viewports = [
    { name: 'desktop', width: 1920, height: 1080 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'mobile', width: 375, height: 667 },
  ];

  const themes = ['light', 'dark'];

  // Screenshot configurations
  const screenshotOptions = {
    fullPage: true,
    animations: 'disabled' as const,
    caret: 'hide' as const,
    mode: 'css' as const,
  };

  test.beforeEach(async ({ page }) => {
    // Set up consistent testing environment
    await page.addInitScript(() => {
      // Disable animations for consistent screenshots
      const style = document.createElement('style');
      style.textContent = `
        *, *::before, *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
        }
      `;
      document.head.appendChild(style);

      // Mock random functions for consistent results
      Math.random = () => 0.5;
      Date.now = () => 1640995200000; // Fixed timestamp

      // Mock performance.now for consistent animations
      performance.now = () => 1000;
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Wait for 3D scene to initialize
    await page.waitForTimeout(3000);
  });

  // Test homepage across different viewports and themes
  for (const viewport of viewports) {
    for (const theme of themes) {
      test(`homepage - ${viewport.name} - ${theme} theme`, async ({ page }) => {
        await page.setViewportSize(viewport);
        
        // Set theme
        await page.evaluate((themeName) => {
          document.documentElement.setAttribute('data-theme', themeName);
        }, theme);

        await page.waitForTimeout(1000); // Allow theme to apply

        // Take screenshot
        await expect(page).toHaveScreenshot(
          `homepage-${viewport.name}-${theme}.png`,
          screenshotOptions
        );
      });
    }
  }

  test.describe('Component Visual Tests', () => {
    
    test('project modal - all states', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      
      // Click on first project to open modal
      const projectPlant = page.locator('[data-testid="project-plant"]').first();
      await projectPlant.click();
      
      // Wait for modal to appear and animate in
      await page.waitForSelector('[data-testid="project-modal"]', { 
        state: 'visible' 
      });
      await page.waitForTimeout(500);
      
      // Screenshot modal
      const modal = page.locator('[data-testid="project-modal"]');
      await expect(modal).toHaveScreenshot('project-modal-default.png');
      
      // Test modal with different project types if available
      const closeButton = page.locator('[data-testid="close-modal"]');
      await closeButton.click();
      await page.waitForTimeout(500);
      
      // Open second project if available
      const projects = page.locator('[data-testid="project-plant"]');
      const projectCount = await projects.count();
      
      if (projectCount > 1) {
        await projects.nth(1).click();
        await page.waitForSelector('[data-testid="project-modal"]', { 
          state: 'visible' 
        });
        await page.waitForTimeout(500);
        
        await expect(page.locator('[data-testid="project-modal"]')).toHaveScreenshot(
          'project-modal-secondary.png'
        );
      }
    });

    test('skill constellation - interaction states', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      
      // Screenshot initial state
      const skillConstellation = page.locator('[data-testid="skill-constellation"]');
      await expect(skillConstellation).toHaveScreenshot('skill-constellation-default.png');
      
      // Click to open skill details
      await skillConstellation.click();
      await page.waitForSelector('[data-testid="skill-details"]', { 
        state: 'visible' 
      });
      await page.waitForTimeout(500);
      
      await expect(page.locator('[data-testid="skill-details"]')).toHaveScreenshot(
        'skill-details-open.png'
      );
    });

    test('navigation overlay - all states', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      
      // Screenshot default navigation
      const navigation = page.locator('[data-testid="navigation-overlay"]');
      await expect(navigation).toHaveScreenshot('navigation-default.png');
      
      // Test mobile navigation if menu toggle exists
      await page.setViewportSize({ width: 375, height: 667 });
      await page.waitForTimeout(500);
      
      const menuToggle = page.locator('[data-testid="menu-toggle"]');
      if (await menuToggle.isVisible()) {
        await menuToggle.click();
        await page.waitForTimeout(500);
        
        await expect(page.locator('[data-testid="mobile-menu"]')).toHaveScreenshot(
          'navigation-mobile-open.png'
        );
      }
    });

    test('settings panel - configuration options', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      
      // Open settings if available
      const settingsButton = page.locator('[data-testid="settings-button"]');
      if (await settingsButton.isVisible()) {
        await settingsButton.click();
        await page.waitForSelector('[data-testid="settings-panel"]', {
          state: 'visible'
        });
        await page.waitForTimeout(500);
        
        await expect(page.locator('[data-testid="settings-panel"]')).toHaveScreenshot(
          'settings-panel-default.png'
        );
        
        // Test different settings states
        const qualityToggle = page.locator('[data-testid="quality-toggle"]');
        if (await qualityToggle.isVisible()) {
          await qualityToggle.click();
          await page.waitForTimeout(300);
          
          await expect(page.locator('[data-testid="settings-panel"]')).toHaveScreenshot(
            'settings-panel-low-quality.png'
          );
        }
      }
    });
  });

  test.describe('Loading States', () => {
    
    test('loading screen variations', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      
      // Intercept network requests to simulate loading
      await page.route('**/api/v1/garden/data', route => {
        // Delay response to capture loading state
        setTimeout(() => route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            projects: [],
            skills: [],
            weather: { condition: 'sunny', temperature: 22 }
          })
        }), 2000);
      });
      
      await page.goto('/');
      
      // Capture loading state
      const loadingScreen = page.locator('[data-testid="loading-screen"]');
      await expect(loadingScreen).toHaveScreenshot('loading-screen.png');
      
      // Wait for loading to complete
      await page.waitForSelector('[data-testid="garden-canvas"]', {
        state: 'visible',
        timeout: 10000
      });
    });

    test('error states', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      
      // Simulate API error
      await page.route('**/api/v1/garden/data', route => 
        route.fulfill({ status: 500, body: 'Internal Server Error' })
      );
      
      await page.goto('/');
      
      // Wait for error state to appear
      await page.waitForSelector('[data-testid="garden-error"]', {
        state: 'visible',
        timeout: 10000
      });
      
      await expect(page.locator('[data-testid="garden-error"]')).toHaveScreenshot(
        'error-state.png'
      );
    });
  });

  test.describe('Weather System Visual Tests', () => {
    
    const weatherConditions = ['sunny', 'rainy', 'cloudy', 'stormy'];
    
    for (const condition of weatherConditions) {
      test(`weather system - ${condition}`, async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 720 });
        
        // Mock weather data
        await page.route('**/api/v1/weather/current', route =>
          route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              condition,
              temperature: 22,
              humidity: 65,
              windSpeed: 8
            })
          })
        );
        
        await page.goto('/');
        await page.waitForSelector('[data-testid="weather-system"]', {
          state: 'visible'
        });
        await page.waitForTimeout(2000); // Allow weather effects to initialize
        
        await expect(page.locator('[data-testid="weather-system"]')).toHaveScreenshot(
          `weather-${condition}.png`
        );
      });
    }
  });

  test.describe('Responsive Design Tests', () => {
    
    const testCases = [
      { name: 'large-desktop', width: 1920, height: 1080 },
      { name: 'desktop', width: 1280, height: 720 },
      { name: 'laptop', width: 1024, height: 768 },
      { name: 'tablet-landscape', width: 1024, height: 768 },
      { name: 'tablet-portrait', width: 768, height: 1024 },
      { name: 'mobile-large', width: 414, height: 896 },
      { name: 'mobile-medium', width: 375, height: 667 },
      { name: 'mobile-small', width: 320, height: 568 },
    ];
    
    for (const testCase of testCases) {
      test(`responsive layout - ${testCase.name}`, async ({ page }) => {
        await page.setViewportSize({ 
          width: testCase.width, 
          height: testCase.height 
        });
        
        await page.waitForTimeout(1000); // Allow layout to adapt
        
        await expect(page).toHaveScreenshot(
          `responsive-${testCase.name}.png`,
          screenshotOptions
        );
      });
    }
  });

  test.describe('High Contrast and Accessibility', () => {
    
    test('high contrast mode', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      
      // Enable high contrast mode
      await page.addInitScript(() => {
        document.documentElement.setAttribute('data-high-contrast', 'true');
      });
      
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      
      await expect(page).toHaveScreenshot(
        'high-contrast-mode.png',
        screenshotOptions
      );
    });

    test('reduced motion mode', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      
      // Set reduced motion preference
      await page.emulateMedia({ reducedMotion: 'reduce' });
      
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      
      await expect(page).toHaveScreenshot(
        'reduced-motion-mode.png',
        screenshotOptions
      );
    });

    test('focus indicators', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Focus on interactive elements and capture focus states
      const focusableElements = [
        '[data-testid="settings-button"]',
        '[data-testid="project-plant"]',
        '[data-testid="navigation-link"]'
      ];
      
      for (const selector of focusableElements) {
        const element = page.locator(selector).first();
        if (await element.isVisible()) {
          await element.focus();
          await page.waitForTimeout(300);
          
          await expect(element).toHaveScreenshot(
            `focus-${selector.replace(/[\[\]"=\-]/g, '')}.png`
          );
        }
      }
    });
  });

  test.describe('Print Styles', () => {
    
    test('print layout', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Emulate print media
      await page.emulateMedia({ media: 'print' });
      await page.waitForTimeout(1000);
      
      await expect(page).toHaveScreenshot(
        'print-layout.png',
        { ...screenshotOptions, fullPage: true }
      );
    });
  });

  test.describe('Cross-Browser Visual Consistency', () => {
    
    // These tests would run across different browsers in CI
    test('browser compatibility - chrome', async ({ page, browserName }) => {
      test.skip(browserName !== 'chromium', 'Chrome-specific test');
      
      await page.setViewportSize({ width: 1280, height: 720 });
      await expect(page).toHaveScreenshot(
        'browser-chrome.png',
        screenshotOptions
      );
    });

    test('browser compatibility - firefox', async ({ page, browserName }) => {
      test.skip(browserName !== 'firefox', 'Firefox-specific test');
      
      await page.setViewportSize({ width: 1280, height: 720 });
      await expect(page).toHaveScreenshot(
        'browser-firefox.png',
        screenshotOptions
      );
    });

    test('browser compatibility - safari', async ({ page, browserName }) => {
      test.skip(browserName !== 'webkit', 'Safari-specific test');
      
      await page.setViewportSize({ width: 1280, height: 720 });
      await expect(page).toHaveScreenshot(
        'browser-safari.png',
        screenshotOptions
      );
    });
  });

  test.describe('Performance Impact Visual Tests', () => {
    
    test('low performance mode visual differences', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      
      // Enable low performance mode
      await page.evaluate(() => {
        if (window.gardenStore) {
          window.gardenStore.getState().setPerformanceMode('low');
        }
      });
      
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(3000);
      
      await expect(page).toHaveScreenshot(
        'low-performance-mode.png',
        screenshotOptions
      );
    });

    test('reduced quality visual comparison', async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
      
      // Set reduced quality settings
      await page.evaluate(() => {
        if (window.gardenStore) {
          const store = window.gardenStore.getState();
          store.setGraphicsQuality('low');
          store.setAnimationQuality('reduced');
        }
      });
      
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(3000);
      
      await expect(page).toHaveScreenshot(
        'reduced-quality-mode.png',
        screenshotOptions
      );
    });
  });
});