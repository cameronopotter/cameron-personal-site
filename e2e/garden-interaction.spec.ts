import { test, expect, Page } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

/**
 * E2E tests for Digital Greenhouse garden interactions
 */
test.describe('Digital Greenhouse - Garden Interactions', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    
    // Wait for the garden to load
    await page.waitForSelector('[data-testid="garden-canvas"]', { 
      state: 'visible',
      timeout: 30000 
    });
    
    // Wait for initial render to complete
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // Allow 3D scene to initialize
  });

  test('should load and render the 3D garden scene', async ({ page }) => {
    // Check that the main canvas is rendered
    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible();
    
    // Check that WebGL context is working
    const webglSupported = await page.evaluate(() => {
      const canvas = document.querySelector('canvas') as HTMLCanvasElement;
      const gl = canvas?.getContext('webgl2') || canvas?.getContext('webgl');
      return gl !== null;
    });
    expect(webglSupported).toBe(true);
    
    // Verify garden components are present
    await expect(page.locator('[data-testid="project-plant"]')).toHaveCount({ min: 1 });
    await expect(page.locator('[data-testid="skill-constellation"]')).toBeVisible();
  });

  test('should handle mouse interactions correctly', async ({ page }) => {
    const canvas = page.locator('canvas');
    
    // Get initial camera position
    const initialCameraPosition = await page.evaluate(() => {
      return window.gardenStore?.getState().camera.position;
    });
    
    // Perform mouse drag to rotate camera
    await canvas.dragTo(canvas, {
      sourcePosition: { x: 100, y: 100 },
      targetPosition: { x: 200, y: 200 }
    });
    
    // Wait for animation to complete
    await page.waitForTimeout(1000);
    
    // Check that camera position changed
    const newCameraPosition = await page.evaluate(() => {
      return window.gardenStore?.getState().camera.position;
    });
    
    expect(newCameraPosition).not.toEqual(initialCameraPosition);
  });

  test('should handle keyboard navigation', async ({ page }) => {
    // Focus on the canvas
    await page.locator('canvas').focus();
    
    // Test arrow key navigation
    await page.keyboard.press('ArrowUp');
    await page.waitForTimeout(500);
    
    await page.keyboard.press('ArrowLeft');
    await page.waitForTimeout(500);
    
    // Should have moved the camera
    const cameraPosition = await page.evaluate(() => {
      return window.gardenStore?.getState().camera.position;
    });
    
    expect(cameraPosition).toBeDefined();
  });

  test('should display project details on interaction', async ({ page }) => {
    // Click on a project plant
    const projectPlant = page.locator('[data-testid="project-plant"]').first();
    await projectPlant.click();
    
    // Wait for modal or tooltip to appear
    await page.waitForSelector('[data-testid="project-modal"]', { 
      state: 'visible',
      timeout: 5000 
    });
    
    // Check modal content
    const modal = page.locator('[data-testid="project-modal"]');
    await expect(modal).toContainText('E2E Test Project');
    await expect(modal.locator('[data-testid="project-description"]')).toBeVisible();
    await expect(modal.locator('[data-testid="project-technologies"]')).toBeVisible();
    
    // Close modal
    await page.locator('[data-testid="close-modal"]').click();
    await expect(modal).not.toBeVisible();
  });

  test('should handle skill constellation interactions', async ({ page }) => {
    // Click on skill constellation
    const skillConstellation = page.locator('[data-testid="skill-constellation"]');
    await skillConstellation.click();
    
    // Wait for skill details to appear
    await page.waitForSelector('[data-testid="skill-details"]', { 
      state: 'visible',
      timeout: 5000 
    });
    
    // Check skill information
    const skillDetails = page.locator('[data-testid="skill-details"]');
    await expect(skillDetails).toContainText(['React', 'Python', 'Three.js']);
    
    // Test skill level indicators
    const skillLevels = page.locator('[data-testid="skill-level"]');
    await expect(skillLevels).toHaveCount({ min: 3 });
  });

  test('should respond to weather changes', async ({ page }) => {
    // Get initial weather state
    const initialWeather = await page.evaluate(() => {
      return window.gardenStore?.getState().weather;
    });
    
    // Trigger weather change (if available in UI)
    const weatherButton = page.locator('[data-testid="weather-toggle"]');
    if (await weatherButton.isVisible()) {
      await weatherButton.click();
      
      // Wait for weather animation
      await page.waitForTimeout(2000);
      
      // Check that weather changed
      const newWeather = await page.evaluate(() => {
        return window.gardenStore?.getState().weather;
      });
      
      expect(newWeather).not.toEqual(initialWeather);
    }
  });

  test('should maintain performance during interactions', async ({ page }) => {
    // Start performance monitoring
    await page.evaluate(() => {
      window.performanceMetrics = {
        frameCount: 0,
        startTime: performance.now(),
        fps: []
      };
      
      function measureFrameRate() {
        const now = performance.now();
        const fps = 1000 / (now - window.performanceMetrics.lastFrame || now);
        window.performanceMetrics.fps.push(fps);
        window.performanceMetrics.lastFrame = now;
        window.performanceMetrics.frameCount++;
        
        if (window.performanceMetrics.frameCount < 60) {
          requestAnimationFrame(measureFrameRate);
        }
      }
      
      requestAnimationFrame(measureFrameRate);
    });
    
    // Perform multiple interactions
    const canvas = page.locator('canvas');
    
    for (let i = 0; i < 10; i++) {
      await canvas.dragTo(canvas, {
        sourcePosition: { x: 100 + i * 10, y: 100 },
        targetPosition: { x: 200 + i * 10, y: 200 }
      });
      await page.waitForTimeout(100);
    }
    
    // Check performance metrics
    const performanceData = await page.evaluate(() => {
      return window.performanceMetrics;
    });
    
    const averageFps = performanceData.fps.reduce((sum, fps) => sum + fps, 0) / performanceData.fps.length;
    
    // Should maintain reasonable FPS
    expect(averageFps).toBeGreaterThan(20);
    expect(performanceData.frameCount).toBeGreaterThan(50);
  });

  test('should handle window resize gracefully', async ({ page }) => {
    // Get initial canvas size
    const initialSize = await page.locator('canvas').boundingBox();
    
    // Resize window
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.waitForTimeout(1000);
    
    // Check that canvas resized
    const newSize = await page.locator('canvas').boundingBox();
    expect(newSize?.width).not.toBe(initialSize?.width);
    
    // Resize back
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(1000);
    
    // Should still be functional
    const canvas = page.locator('canvas');
    await canvas.click();
    await expect(canvas).toBeVisible();
  });

  test('should load garden data progressively', async ({ page }) => {
    // Check loading states
    const loadingIndicator = page.locator('[data-testid="garden-loading"]');
    
    // Should show loading initially (if it exists)
    if (await loadingIndicator.isVisible()) {
      await expect(loadingIndicator).not.toBeVisible({ timeout: 10000 });
    }
    
    // Check that data loaded
    await page.waitForFunction(() => {
      return window.gardenStore?.getState().projects.length > 0;
    }, { timeout: 15000 });
    
    const projectCount = await page.evaluate(() => {
      return window.gardenStore?.getState().projects.length;
    });
    
    expect(projectCount).toBeGreaterThan(0);
  });

  test('should handle error states gracefully', async ({ page }) => {
    // Simulate network error by blocking API calls
    await page.route('**/api/v1/garden/**', route => route.abort());
    
    // Reload page
    await page.reload();
    
    // Should show error state
    await page.waitForSelector('[data-testid="garden-error"]', { 
      state: 'visible',
      timeout: 10000 
    });
    
    const errorMessage = page.locator('[data-testid="garden-error"]');
    await expect(errorMessage).toContainText(['error', 'failed', 'loading']);
    
    // Should have retry functionality
    const retryButton = page.locator('[data-testid="retry-button"]');
    if (await retryButton.isVisible()) {
      // Unblock API calls
      await page.unroute('**/api/v1/garden/**');
      
      // Click retry
      await retryButton.click();
      
      // Should recover
      await page.waitForSelector('[data-testid="garden-canvas"]', { 
        state: 'visible',
        timeout: 15000 
      });
    }
  });
});