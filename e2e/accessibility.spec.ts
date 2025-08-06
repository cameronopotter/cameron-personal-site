import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * Accessibility testing for Digital Greenhouse
 * @accessibility
 */
test.describe('Digital Greenhouse - Accessibility Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should pass basic accessibility checks', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should have proper ARIA labels and roles', async ({ page }) => {
    // Check main navigation
    const nav = page.locator('nav[role="navigation"]');
    await expect(nav).toBeVisible();
    
    // Check that interactive elements have proper labels
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < buttonCount; i++) {
      const button = buttons.nth(i);
      if (await button.isVisible()) {
        // Button should have accessible name (aria-label, aria-labelledby, or text content)
        const accessibleName = await button.evaluate(el => {
          return el.getAttribute('aria-label') || 
                 el.getAttribute('aria-labelledby') || 
                 el.textContent?.trim();
        });
        expect(accessibleName).toBeTruthy();
      }
    }
    
    // Check canvas accessibility
    const canvas = page.locator('canvas');
    const canvasLabel = await canvas.getAttribute('aria-label');
    expect(canvasLabel).toBeTruthy();
    expect(canvasLabel).toContain('3D garden');
  });

  test('should support keyboard navigation', async ({ page }) => {
    // Test tab navigation
    await page.keyboard.press('Tab');
    
    // Should focus on first interactive element
    const firstFocusable = await page.evaluate(() => {
      return document.activeElement?.tagName;
    });
    expect(['BUTTON', 'A', 'INPUT', 'CANVAS']).toContain(firstFocusable);
    
    // Continue tabbing through interactive elements
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      
      const focused = await page.evaluate(() => {
        const el = document.activeElement;
        return {
          tagName: el?.tagName,
          hasVisibleFocus: getComputedStyle(el).outlineStyle !== 'none' ||
                           getComputedStyle(el).boxShadow.includes('focus')
        };
      });
      
      // Interactive elements should show focus indicator
      if (['BUTTON', 'A', 'INPUT', 'CANVAS'].includes(focused.tagName)) {
        expect(focused.hasVisibleFocus).toBeTruthy();
      }
    }
  });

  test('should support screen reader navigation', async ({ page }) => {
    // Test heading structure
    const headings = page.locator('h1, h2, h3, h4, h5, h6');
    const headingCount = await headings.count();
    
    expect(headingCount).toBeGreaterThan(0);
    
    // Check heading hierarchy
    const headingLevels = await headings.evaluateAll(headings => {
      return headings.map(h => parseInt(h.tagName.charAt(1)));
    });
    
    // Should start with h1
    expect(headingLevels[0]).toBe(1);
    
    // Check landmarks
    const landmarks = await page.locator('[role="main"], [role="navigation"], [role="banner"], [role="contentinfo"]').count();
    expect(landmarks).toBeGreaterThan(0);
    
    // Check skip links
    const skipLink = page.locator('a[href="#main-content"]');
    if (await skipLink.count() > 0) {
      await expect(skipLink).toHaveAttribute('class', /skip-link/);
    }
  });

  test('should provide alternative text for visual content', async ({ page }) => {
    // Check images have alt text
    const images = page.locator('img');
    const imageCount = await images.count();
    
    for (let i = 0; i < imageCount; i++) {
      const img = images.nth(i);
      const alt = await img.getAttribute('alt');
      expect(alt).not.toBeNull();
    }
    
    // Check canvas has description
    const canvas = page.locator('canvas');
    const ariaDescribedBy = await canvas.getAttribute('aria-describedby');
    
    if (ariaDescribedBy) {
      const description = page.locator(`#${ariaDescribedBy}`);
      await expect(description).toBeVisible();
      await expect(description).not.toBeEmpty();
    }
  });

  test('should handle high contrast mode', async ({ page }) => {
    // Simulate high contrast mode
    await page.emulateMedia({ colorScheme: 'dark', reducedMotion: 'reduce' });
    
    // Check that text remains readable
    const textElements = page.locator('p, span, div:has-text(".")').first();
    const computedStyle = await textElements.evaluate(el => {
      const style = getComputedStyle(el);
      return {
        color: style.color,
        backgroundColor: style.backgroundColor,
        fontSize: style.fontSize
      };
    });
    
    expect(computedStyle.color).not.toBe(computedStyle.backgroundColor);
    
    // Test with light mode
    await page.emulateMedia({ colorScheme: 'light' });
    await page.waitForTimeout(1000);
    
    // Should still be accessible
    const lightModeResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    
    expect(lightModeResults.violations).toEqual([]);
  });

  test('should support reduced motion preferences', async ({ page }) => {
    // Test with reduced motion
    await page.emulateMedia({ reducedMotion: 'reduce' });
    
    // Check that animations are disabled or reduced
    const animatedElements = page.locator('[data-testid*="animation"], .animate, [class*="motion"]');
    const elementCount = await animatedElements.count();
    
    for (let i = 0; i < elementCount; i++) {
      const element = animatedElements.nth(i);
      const animationDuration = await element.evaluate(el => {
        return getComputedStyle(el).animationDuration;
      });
      
      // Should have very short or no animation duration
      expect(['0s', '0.01s']).toContain(animationDuration);
    }
  });

  test('should provide proper focus management', async ({ page }) => {
    // Test modal focus management
    const projectPlant = page.locator('[data-testid="project-plant"]').first();
    
    if (await projectPlant.count() > 0) {
      await projectPlant.click();
      
      // Wait for modal
      const modal = page.locator('[data-testid="project-modal"]');
      if (await modal.isVisible()) {
        // Focus should be trapped in modal
        const modalFirstFocusable = modal.locator('button, a, input, [tabindex="0"]').first();
        await expect(modalFirstFocusable).toBeFocused();
        
        // Tab should stay within modal
        await page.keyboard.press('Tab');
        const focusedElement = await page.evaluate(() => document.activeElement);
        const isWithinModal = await modal.evaluate((modal, focused) => {
          return modal.contains(focused);
        }, focusedElement);
        
        expect(isWithinModal).toBe(true);
        
        // Escape should close modal and return focus
        await page.keyboard.press('Escape');
        await expect(modal).not.toBeVisible();
        await expect(projectPlant).toBeFocused();
      }
    }
  });

  test('should provide adequate color contrast', async ({ page }) => {
    const colorContrastResults = await new AxeBuilder({ page })
      .withTags(['wcag2aa'])
      .include('[data-testid="main-content"]')
      .analyze();
    
    const contrastViolations = colorContrastResults.violations.filter(
      violation => violation.id === 'color-contrast'
    );
    
    expect(contrastViolations).toEqual([]);
  });

  test('should support voice navigation announcements', async ({ page }) => {
    // Check for live regions
    const liveRegions = page.locator('[aria-live], [role="status"], [role="alert"]');
    const liveRegionCount = await liveRegions.count();
    
    expect(liveRegionCount).toBeGreaterThan(0);
    
    // Test status announcements
    const statusRegion = page.locator('[aria-live="polite"]');
    if (await statusRegion.count() > 0) {
      // Trigger an action that should announce status
      await page.locator('[data-testid="settings-button"]').click();
      
      // Check if status was announced
      await page.waitForTimeout(1000);
      const statusText = await statusRegion.textContent();
      expect(statusText?.length).toBeGreaterThan(0);
    }
  });

  test('should handle form accessibility', async ({ page }) => {
    // Look for forms
    const forms = page.locator('form');
    const formCount = await forms.count();
    
    for (let i = 0; i < formCount; i++) {
      const form = forms.nth(i);
      
      // Check form inputs have labels
      const inputs = form.locator('input, textarea, select');
      const inputCount = await inputs.count();
      
      for (let j = 0; j < inputCount; j++) {
        const input = inputs.nth(j);
        const inputId = await input.getAttribute('id');
        const ariaLabel = await input.getAttribute('aria-label');
        const ariaLabelledBy = await input.getAttribute('aria-labelledby');
        
        // Should have some form of label
        const hasLabel = inputId ? await page.locator(`label[for="${inputId}"]`).count() > 0 : false;
        const hasAccessibleName = hasLabel || ariaLabel || ariaLabelledBy;
        
        expect(hasAccessibleName).toBe(true);
      }
      
      // Check for fieldsets if multiple related inputs
      if (inputCount > 3) {
        const fieldsets = form.locator('fieldset');
        const fieldsetCount = await fieldsets.count();
        
        if (fieldsetCount > 0) {
          // Fieldsets should have legends
          const legends = form.locator('legend');
          await expect(legends.first()).toBeVisible();
        }
      }
    }
  });

  test('should announce dynamic content changes', async ({ page }) => {
    // Monitor for dynamic content
    const notifications = page.locator('[data-testid="notification-system"]');
    
    if (await notifications.count() > 0) {
      // Should have proper ARIA attributes
      const ariaLive = await notifications.getAttribute('aria-live');
      expect(['polite', 'assertive']).toContain(ariaLive);
      
      // Test notification announcement
      // This would depend on your actual notification system
      await page.evaluate(() => {
        // Simulate showing a notification
        if (window.notificationSystem) {
          window.notificationSystem.show('Test notification for screen readers');
        }
      });
      
      await page.waitForTimeout(500);
      const notificationText = await notifications.textContent();
      expect(notificationText).toContain('Test notification');
    }
  });
});