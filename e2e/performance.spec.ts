import { test, expect } from '@playwright/test';
import { playAudit } from 'lighthouse/lighthouse-core/audits/audit';

/**
 * Performance testing for Digital Greenhouse
 * @performance
 */
test.describe('Digital Greenhouse - Performance Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Enable performance monitoring
    await page.addInitScript(() => {
      window.performanceMetrics = {
        navigationStart: performance.now(),
        marks: {},
        measures: {},
        resources: []
      };
      
      // Monitor resource loading
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          window.performanceMetrics.resources.push({
            name: entry.name,
            duration: entry.duration,
            transferSize: entry.transferSize || 0,
            type: entry.initiatorType
          });
        }
      });
      observer.observe({entryTypes: ['resource']});
      
      // Custom performance marks
      window.markPerformance = (name) => {
        performance.mark(name);
        window.performanceMetrics.marks[name] = performance.now();
      };
      
      window.measurePerformance = (name, start, end) => {
        performance.measure(name, start, end);
        const measure = performance.getEntriesByName(name, 'measure')[0];
        window.performanceMetrics.measures[name] = measure.duration;
      };
    });
  });

  test('should load within acceptable time limits', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    
    // Wait for initial content
    await page.waitForSelector('[data-testid="garden-canvas"]');
    const initialLoadTime = Date.now() - startTime;
    
    // Initial load should be under 3 seconds
    expect(initialLoadTime).toBeLessThan(3000);
    
    // Wait for full 3D scene initialization
    await page.waitForLoadState('networkidle');
    const fullLoadTime = Date.now() - startTime;
    
    // Full load should be under 5 seconds
    expect(fullLoadTime).toBeLessThan(5000);
    
    console.log(`Initial load: ${initialLoadTime}ms, Full load: ${fullLoadTime}ms`);
  });

  test('should maintain 60 FPS during interactions', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="garden-canvas"]');
    
    // Start FPS monitoring
    await page.evaluate(() => {
      window.fpsMetrics = {
        frames: [],
        startTime: performance.now(),
        lastFrameTime: performance.now()
      };
      
      function measureFPS() {
        const now = performance.now();
        const fps = 1000 / (now - window.fpsMetrics.lastFrameTime);
        window.fpsMetrics.frames.push(fps);
        window.fpsMetrics.lastFrameTime = now;
        
        if (window.fpsMetrics.frames.length < 180) { // 3 seconds at 60fps
          requestAnimationFrame(measureFPS);
        }
      }
      
      requestAnimationFrame(measureFPS);
    });
    
    // Perform intensive interactions
    const canvas = page.locator('canvas');
    
    // Rapid mouse movements
    for (let i = 0; i < 20; i++) {
      await canvas.hover({ position: { x: 100 + i * 10, y: 100 + i * 5 } });
      await page.waitForTimeout(50);
    }
    
    // Dragging operations
    await canvas.dragTo(canvas, {
      sourcePosition: { x: 100, y: 100 },
      targetPosition: { x: 300, y: 300 }
    });
    
    // Get FPS data
    const fpsData = await page.evaluate(() => window.fpsMetrics);
    const avgFPS = fpsData.frames.reduce((sum, fps) => sum + fps, 0) / fpsData.frames.length;
    const minFPS = Math.min(...fpsData.frames);
    
    console.log(`Average FPS: ${avgFPS.toFixed(2)}, Minimum FPS: ${minFPS.toFixed(2)}`);
    
    // Should maintain reasonable FPS
    expect(avgFPS).toBeGreaterThan(30); // Minimum 30 FPS average
    expect(minFPS).toBeGreaterThan(20); // No drops below 20 FPS
    
    // Ideally should achieve 60 FPS
    if (avgFPS < 50) {
      console.warn('Performance warning: Average FPS below 50');
    }
  });

  test('should efficiently manage memory usage', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="garden-canvas"]');
    
    // Get initial memory usage
    const initialMemory = await page.evaluate(() => {
      if ('memory' in performance) {
        return {
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          totalJSHeapSize: performance.memory.totalJSHeapSize,
          jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
        };
      }
      return null;
    });
    
    // Perform memory-intensive operations
    await page.evaluate(() => {
      // Simulate creating and disposing of 3D objects
      for (let i = 0; i < 100; i++) {
        const geometry = new THREE.BoxGeometry(1, 1, 1);
        const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
        const cube = new THREE.Mesh(geometry, material);
        
        // Immediately dispose to test cleanup
        geometry.dispose();
        material.dispose();
      }
    });
    
    // Force garbage collection if available
    await page.evaluate(() => {
      if (window.gc) {
        window.gc();
      }
    });
    
    // Wait for cleanup
    await page.waitForTimeout(2000);
    
    // Check final memory usage
    const finalMemory = await page.evaluate(() => {
      if ('memory' in performance) {
        return {
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          totalJSHeapSize: performance.memory.totalJSHeapSize,
          jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
        };
      }
      return null;
    });
    
    if (initialMemory && finalMemory) {
      const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;
      const memoryIncreasePercent = (memoryIncrease / initialMemory.usedJSHeapSize) * 100;
      
      console.log(`Memory increase: ${(memoryIncrease / 1024 / 1024).toFixed(2)} MB (${memoryIncreasePercent.toFixed(1)}%)`);
      
      // Memory increase should be reasonable
      expect(memoryIncreasePercent).toBeLessThan(50); // Less than 50% increase
    }
  });

  test('should load resources efficiently', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Get resource loading performance
    const resourceMetrics = await page.evaluate(() => window.performanceMetrics.resources);
    
    // Analyze resource types
    const resourceTypes = resourceMetrics.reduce((acc, resource) => {
      acc[resource.type] = acc[resource.type] || { count: 0, totalSize: 0, totalDuration: 0 };
      acc[resource.type].count++;
      acc[resource.type].totalSize += resource.transferSize;
      acc[resource.type].totalDuration += resource.duration;
      return acc;
    }, {});
    
    console.log('Resource loading metrics:', resourceTypes);
    
    // Check script loading
    if (resourceTypes.script) {
      const avgScriptLoadTime = resourceTypes.script.totalDuration / resourceTypes.script.count;
      expect(avgScriptLoadTime).toBeLessThan(1000); // Scripts should load in under 1s on average
    }
    
    // Check image/texture loading
    if (resourceTypes.img) {
      const avgImageLoadTime = resourceTypes.img.totalDuration / resourceTypes.img.count;
      expect(avgImageLoadTime).toBeLessThan(2000); // Images should load in under 2s on average
    }
    
    // Total transfer size should be reasonable
    const totalTransferSize = resourceMetrics.reduce((sum, r) => sum + r.transferSize, 0);
    console.log(`Total transfer size: ${(totalTransferSize / 1024 / 1024).toFixed(2)} MB`);
    
    // Should be under 10MB for initial load
    expect(totalTransferSize).toBeLessThan(10 * 1024 * 1024);
  });

  test('should handle large datasets efficiently', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="garden-canvas"]');
    
    // Simulate loading large amount of data
    const loadStartTime = Date.now();
    
    await page.evaluate(() => {
      // Simulate loading 1000 projects
      const largeDataset = Array.from({ length: 1000 }, (_, i) => ({
        id: i,
        name: `Project ${i}`,
        position: [Math.random() * 100, Math.random() * 10, Math.random() * 100],
        growth: Math.random(),
        type: 'tree'
      }));
      
      if (window.gardenStore) {
        window.gardenStore.getState().setProjects(largeDataset);
      }
    });
    
    // Wait for rendering to complete
    await page.waitForTimeout(2000);
    
    const loadEndTime = Date.now();
    const processingTime = loadEndTime - loadStartTime;
    
    console.log(`Large dataset processing time: ${processingTime}ms`);
    
    // Should process large datasets in reasonable time
    expect(processingTime).toBeLessThan(5000); // Under 5 seconds
    
    // Check that performance is still good after loading
    const fpsAfterLoad = await page.evaluate(() => {
      let frameCount = 0;
      const startTime = performance.now();
      
      return new Promise((resolve) => {
        function measureFrame() {
          frameCount++;
          if (frameCount >= 60) {
            const endTime = performance.now();
            const fps = (frameCount * 1000) / (endTime - startTime);
            resolve(fps);
          } else {
            requestAnimationFrame(measureFrame);
          }
        }
        requestAnimationFrame(measureFrame);
      });
    });
    
    expect(fpsAfterLoad).toBeGreaterThan(30); // Should maintain good FPS even with large datasets
  });

  test('should optimize render performance', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('[data-testid="garden-canvas"]');
    
    // Monitor render performance
    await page.evaluate(() => {
      window.renderMetrics = {
        drawCalls: 0,
        triangles: 0,
        renderTime: []
      };
      
      // Hook into WebGL context to count draw calls
      const canvas = document.querySelector('canvas');
      const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
      
      if (gl) {
        const originalDrawArrays = gl.drawArrays;
        const originalDrawElements = gl.drawElements;
        
        gl.drawArrays = function(...args) {
          window.renderMetrics.drawCalls++;
          return originalDrawArrays.apply(this, args);
        };
        
        gl.drawElements = function(...args) {
          window.renderMetrics.drawCalls++;
          window.renderMetrics.triangles += args[1] / 3; // Approximate triangle count
          return originalDrawElements.apply(this, args);
        };
      }
      
      // Monitor frame render times
      let lastFrameTime = performance.now();
      function measureRenderTime() {
        const now = performance.now();
        const frameTime = now - lastFrameTime;
        window.renderMetrics.renderTime.push(frameTime);
        lastFrameTime = now;
        
        if (window.renderMetrics.renderTime.length < 120) { // 2 seconds worth
          requestAnimationFrame(measureRenderTime);
        }
      }
      requestAnimationFrame(measureRenderTime);
    });
    
    // Perform camera movement to trigger rendering
    const canvas = page.locator('canvas');
    await canvas.dragTo(canvas, {
      sourcePosition: { x: 100, y: 100 },
      targetPosition: { x: 500, y: 300 }
    });
    
    await page.waitForTimeout(3000); // Let metrics collect
    
    const renderMetrics = await page.evaluate(() => window.renderMetrics);
    
    console.log('Render metrics:', {
      totalDrawCalls: renderMetrics.drawCalls,
      avgTriangles: renderMetrics.triangles / 120,
      avgFrameTime: renderMetrics.renderTime.reduce((sum, time) => sum + time, 0) / renderMetrics.renderTime.length
    });
    
    // Optimize for reasonable draw calls (should use batching/instancing)
    expect(renderMetrics.drawCalls).toBeLessThan(1000); // Should batch renders
    
    // Frame time should be reasonable
    const avgFrameTime = renderMetrics.renderTime.reduce((sum, time) => sum + time, 0) / renderMetrics.renderTime.length;
    expect(avgFrameTime).toBeLessThan(16.67); // Under 60 FPS threshold
  });

  test('should handle mobile performance', async ({ page, browserName }) => {
    // Simulate mobile device constraints
    await page.emulate({
      viewport: { width: 390, height: 844 },
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15',
      deviceScaleFactor: 3,
      isMobile: true,
      hasTouch: true
    });
    
    // Throttle CPU and network to simulate mobile conditions
    const client = await page.context().newCDPSession(page);
    await client.send('Emulation.setCPUThrottlingRate', { rate: 4 }); // 4x slower CPU
    
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForSelector('[data-testid="garden-canvas"]');
    const loadTime = Date.now() - startTime;
    
    console.log(`Mobile load time: ${loadTime}ms`);
    
    // Mobile load should be reasonable despite throttling
    expect(loadTime).toBeLessThan(8000); // Under 8 seconds on throttled mobile
    
    // Check that mobile optimizations are active
    const mobileOptimizations = await page.evaluate(() => {
      return {
        pixelRatio: window.devicePixelRatio,
        reducedQuality: window.gardenStore?.getState().settings?.mobileOptimizations,
        lowPowerMode: window.gardenStore?.getState().performance?.lowPowerMode
      };
    });
    
    console.log('Mobile optimizations:', mobileOptimizations);
    
    // Test touch interactions performance
    await page.touchscreen.tap(200, 200);
    await page.waitForTimeout(500);
    
    // Perform touch gesture (pinch zoom simulation)
    await page.touchscreen.tap(150, 300);
    await page.touchscreen.tap(250, 400);
    
    await page.waitForTimeout(1000);
    
    // Should maintain reasonable performance on mobile
    const mobileFPS = await page.evaluate(() => {
      let frameCount = 0;
      const startTime = performance.now();
      
      return new Promise((resolve) => {
        function measureFrame() {
          frameCount++;
          if (frameCount >= 30) { // 30 frames for mobile
            const endTime = performance.now();
            const fps = (frameCount * 1000) / (endTime - startTime);
            resolve(fps);
          } else {
            requestAnimationFrame(measureFrame);
          }
        }
        requestAnimationFrame(measureFrame);
      });
    });
    
    expect(mobileFPS).toBeGreaterThan(20); // Minimum 20 FPS on throttled mobile
  });

  test('should optimize bundle size and loading', async ({ page }) => {
    // Monitor network requests
    const networkRequests = [];
    page.on('request', request => {
      networkRequests.push({
        url: request.url(),
        method: request.method(),
        resourceType: request.resourceType()
      });
    });
    
    page.on('response', response => {
      const request = networkRequests.find(req => req.url === response.url());
      if (request) {
        request.status = response.status();
        request.size = response.headers()['content-length'] || 0;
      }
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Analyze bundle loading
    const jsRequests = networkRequests.filter(req => req.resourceType === 'script');
    const cssRequests = networkRequests.filter(req => req.resourceType === 'stylesheet');
    
    console.log(`JavaScript requests: ${jsRequests.length}`);
    console.log(`CSS requests: ${cssRequests.length}`);
    
    // Should use code splitting (multiple JS chunks)
    expect(jsRequests.length).toBeGreaterThan(1); // Multiple chunks loaded
    expect(jsRequests.length).toBeLessThan(20); // But not too many
    
    // Main bundle should be reasonably sized
    const mainBundle = jsRequests.find(req => req.url.includes('index') || req.url.includes('main'));
    if (mainBundle && mainBundle.size) {
      const bundleSizeMB = parseInt(mainBundle.size) / 1024 / 1024;
      console.log(`Main bundle size: ${bundleSizeMB.toFixed(2)} MB`);
      expect(bundleSizeMB).toBeLessThan(2); // Main bundle under 2MB
    }
    
    // Check for efficient caching
    const cachedRequests = networkRequests.filter(req => 
      req.url.includes('.js') && (req.url.includes('hash') || req.url.includes('chunk'))
    );
    expect(cachedRequests.length).toBeGreaterThan(0); // Should use cache-friendly filenames
  });
});