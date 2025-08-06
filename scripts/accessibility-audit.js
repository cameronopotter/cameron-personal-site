#!/usr/bin/env node

/**
 * Comprehensive Accessibility Audit Script for Digital Greenhouse
 * Uses multiple tools to ensure WCAG compliance and accessibility best practices
 */

const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const puppeteer = require('puppeteer');
const pa11y = require('pa11y');
const { AxePuppeteer } = require('@axe-core/puppeteer');

// Configuration
const CONFIG = {
  baseUrl: process.env.BASE_URL || 'http://localhost:3000',
  outputDir: './accessibility-results',
  
  // Test URLs to audit
  urls: [
    '/',
    '/projects',
    '/skills',
    '/about',
    '/contact'
  ],
  
  // Accessibility standards
  standards: ['WCAG2A', 'WCAG2AA', 'WCAG2AAA'],
  
  // Viewport sizes to test
  viewports: [
    { name: 'desktop', width: 1280, height: 720 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'mobile', width: 375, height: 667 }
  ],
  
  // Pa11y configuration
  pa11yConfig: {
    standard: 'WCAG2AA',
    includeNotices: false,
    includeWarnings: true,
    chromeLaunchConfig: {
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-web-security'
      ]
    },
    wait: 3000
  },
  
  // Axe configuration
  axeConfig: {
    tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
    rules: {
      'color-contrast': { enabled: true },
      'keyboard-navigation': { enabled: true },
      'focus-order': { enabled: true },
      'aria-labels': { enabled: true },
      'landmark-roles': { enabled: true }
    }
  }
};

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m'
};

/**
 * Colored console logging
 */
function log(message, color = 'white') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

/**
 * Ensure output directory exists
 */
async function ensureOutputDir() {
  try {
    await fs.mkdir(CONFIG.outputDir, { recursive: true });
  } catch (error) {
    // Directory already exists, continue
  }
}

/**
 * Wait for server to be ready
 */
async function waitForServer(url, timeout = 30000) {
  const start = Date.now();
  
  while (Date.now() - start < timeout) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        return true;
      }
    } catch (error) {
      // Server not ready yet
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  throw new Error(`Server not ready at ${url} after ${timeout}ms`);
}

/**
 * Run Axe accessibility tests
 */
async function runAxeTests() {
  log('🔍 Running Axe accessibility tests...', 'blue');
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage']
  });
  
  const results = [];
  
  try {
    for (const viewport of CONFIG.viewports) {
      log(`📱 Testing viewport: ${viewport.name} (${viewport.width}x${viewport.height})`, 'cyan');
      
      for (const urlPath of CONFIG.urls) {
        const url = `${CONFIG.baseUrl}${urlPath}`;
        log(`🌐 Testing URL: ${url}`, 'white');
        
        const page = await browser.newPage();
        await page.setViewport(viewport);
        
        try {
          await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });
          
          // Wait for dynamic content to load
          await page.waitForTimeout(3000);
          
          // Run Axe tests
          const axeResults = await new AxePuppeteer(page)
            .withTags(CONFIG.axeConfig.tags)
            .analyze();
          
          results.push({
            url: urlPath,
            viewport: viewport.name,
            timestamp: new Date().toISOString(),
            violations: axeResults.violations,
            passes: axeResults.passes.length,
            incomplete: axeResults.incomplete,
            inapplicable: axeResults.inapplicable.length
          });
          
          // Log immediate results
          if (axeResults.violations.length > 0) {
            log(`❌ Found ${axeResults.violations.length} violations for ${urlPath} on ${viewport.name}`, 'red');
            axeResults.violations.forEach(violation => {
              log(`   - ${violation.id}: ${violation.description}`, 'yellow');
            });
          } else {
            log(`✅ No violations found for ${urlPath} on ${viewport.name}`, 'green');
          }
          
        } catch (error) {
          log(`❌ Error testing ${url}: ${error.message}`, 'red');
          results.push({
            url: urlPath,
            viewport: viewport.name,
            timestamp: new Date().toISOString(),
            error: error.message,
            violations: [],
            passes: 0,
            incomplete: [],
            inapplicable: 0
          });
        } finally {
          await page.close();
        }
      }
    }
  } finally {
    await browser.close();
  }
  
  // Save results
  const outputPath = path.join(CONFIG.outputDir, 'axe-results.json');
  await fs.writeFile(outputPath, JSON.stringify(results, null, 2));
  
  log(`📊 Axe results saved to ${outputPath}`, 'green');
  
  return results;
}

/**
 * Run Pa11y accessibility tests
 */
async function runPa11yTests() {
  log('🔍 Running Pa11y accessibility tests...', 'blue');
  
  const results = [];
  
  for (const urlPath of CONFIG.urls) {
    const url = `${CONFIG.baseUrl}${urlPath}`;
    log(`🌐 Testing URL: ${url}`, 'white');
    
    try {
      const result = await pa11y(url, {
        ...CONFIG.pa11yConfig,
        actions: [
          'wait for element body to be visible',
          'wait for 3000'
        ]
      });
      
      results.push({
        url: urlPath,
        timestamp: new Date().toISOString(),
        issues: result.issues,
        pageUrl: result.pageUrl,
        title: result.title
      });
      
      // Log immediate results
      const errors = result.issues.filter(issue => issue.type === 'error');
      const warnings = result.issues.filter(issue => issue.type === 'warning');
      
      if (errors.length > 0) {
        log(`❌ Found ${errors.length} errors for ${urlPath}`, 'red');
      }
      
      if (warnings.length > 0) {
        log(`⚠️  Found ${warnings.length} warnings for ${urlPath}`, 'yellow');
      }
      
      if (errors.length === 0 && warnings.length === 0) {
        log(`✅ No issues found for ${urlPath}`, 'green');
      }
      
    } catch (error) {
      log(`❌ Error testing ${url}: ${error.message}`, 'red');
      results.push({
        url: urlPath,
        timestamp: new Date().toISOString(),
        error: error.message,
        issues: []
      });
    }
  }
  
  // Save results
  const outputPath = path.join(CONFIG.outputDir, 'pa11y-results.json');
  await fs.writeFile(outputPath, JSON.stringify(results, null, 2));
  
  log(`📊 Pa11y results saved to ${outputPath}`, 'green');
  
  return results;
}

/**
 * Generate comprehensive accessibility report
 */
async function generateReport(axeResults, pa11yResults) {
  log('📋 Generating comprehensive accessibility report...', 'blue');
  
  const timestamp = new Date().toISOString();
  const totalAxeViolations = axeResults.reduce((sum, result) => sum + result.violations.length, 0);
  const totalPa11yIssues = pa11yResults.reduce((sum, result) => sum + result.issues.length, 0);
  
  // Generate summary statistics
  const summary = {
    timestamp,
    totalUrls: CONFIG.urls.length,
    totalViewports: CONFIG.viewports.length,
    axe: {
      totalViolations: totalAxeViolations,
      violationsByUrl: axeResults.reduce((acc, result) => {
        acc[result.url] = acc[result.url] || 0;
        acc[result.url] += result.violations.length;
        return acc;
      }, {}),
      violationsByType: axeResults.reduce((acc, result) => {
        result.violations.forEach(violation => {
          acc[violation.id] = acc[violation.id] || 0;
          acc[violation.id]++;
        });
        return acc;
      }, {})
    },
    pa11y: {
      totalIssues: totalPa11yIssues,
      issuesByUrl: pa11yResults.reduce((acc, result) => {
        acc[result.url] = result.issues.length;
        return acc;
      }, {}),
      issuesByType: pa11yResults.reduce((acc, result) => {
        result.issues.forEach(issue => {
          acc[issue.type] = acc[issue.type] || 0;
          acc[issue.type]++;
        });
        return acc;
      }, {})
    }
  };
  
  // Generate HTML report
  const htmlReport = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Greenhouse Accessibility Audit Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: #2196F3; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .summary { background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .section { background: white; margin: 20px 0; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .violation { margin: 10px 0; padding: 15px; border-left: 4px solid #f44336; background: #ffebee; }
        .warning { margin: 10px 0; padding: 15px; border-left: 4px solid #ff9800; background: #fff3e0; }
        .success { margin: 10px 0; padding: 15px; border-left: 4px solid #4caf50; background: #e8f5e8; }
        .metric { display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 5px; text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; color: #2196F3; }
        .metric-label { color: #666; }
        .chart { margin: 20px 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .error { color: #f44336; }
        .warning-text { color: #ff9800; }
        .success-text { color: #4caf50; }
        .recommendations { background: #e3f2fd; padding: 15px; border-radius: 5px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌱 Digital Greenhouse Accessibility Audit Report</h1>
        <p>Generated on: ${new Date(timestamp).toLocaleString()}</p>
        <p>Standards: WCAG 2.1 AA compliance</p>
    </div>

    <div class="summary">
        <h2>📊 Summary</h2>
        <div>
            <div class="metric">
                <div class="metric-value">${CONFIG.urls.length}</div>
                <div class="metric-label">URLs Tested</div>
            </div>
            <div class="metric">
                <div class="metric-value">${CONFIG.viewports.length}</div>
                <div class="metric-label">Viewports</div>
            </div>
            <div class="metric">
                <div class="metric-value ${totalAxeViolations === 0 ? 'success-text' : 'error'}">${totalAxeViolations}</div>
                <div class="metric-label">Axe Violations</div>
            </div>
            <div class="metric">
                <div class="metric-value ${totalPa11yIssues === 0 ? 'success-text' : 'error'}">${totalPa11yIssues}</div>
                <div class="metric-label">Pa11y Issues</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>🔍 Axe Results</h2>
        ${axeResults.map(result => `
            <div class="violation">
                <h3>${result.url} - ${result.viewport}</h3>
                <p><strong>Violations:</strong> ${result.violations.length}</p>
                <p><strong>Passes:</strong> ${result.passes}</p>
                ${result.violations.map(violation => `
                    <div style="margin-left: 20px; margin-top: 10px;">
                        <strong>${violation.id}:</strong> ${violation.description}<br>
                        <em>Impact: ${violation.impact} | Nodes: ${violation.nodes.length}</em>
                    </div>
                `).join('')}
            </div>
        `).join('')}
    </div>

    <div class="section">
        <h2>🔍 Pa11y Results</h2>
        ${pa11yResults.map(result => `
            <div class="violation">
                <h3>${result.url}</h3>
                <p><strong>Total Issues:</strong> ${result.issues.length}</p>
                ${result.issues.map(issue => `
                    <div style="margin-left: 20px; margin-top: 10px;" class="${issue.type}">
                        <strong>${issue.type.toUpperCase()}:</strong> ${issue.message}<br>
                        <em>Code: ${issue.code} | Selector: ${issue.selector}</em>
                    </div>
                `).join('')}
            </div>
        `).join('')}
    </div>

    <div class="section recommendations">
        <h2>💡 Recommendations</h2>
        <ul>
            <li>Review and fix all critical violations marked as "error" priority</li>
            <li>Ensure proper color contrast ratios (4.5:1 for normal text, 3:1 for large text)</li>
            <li>Verify all interactive elements are keyboard accessible</li>
            <li>Check that all form fields have proper labels</li>
            <li>Ensure heading hierarchy is logical and sequential</li>
            <li>Add ARIA labels where necessary for complex components</li>
            <li>Test with actual screen readers for real-world validation</li>
            <li>Consider implementing skip navigation links</li>
            <li>Ensure focus indicators are visible and high contrast</li>
            <li>Test with keyboard-only navigation</li>
        </ul>
    </div>

    <div class="section">
        <h2>📈 Trend Analysis</h2>
        <p>This section would show accessibility trends over time in a production system.</p>
        <p>Consider integrating with your CI/CD pipeline to track improvements and regressions.</p>
    </div>
</body>
</html>
`;
  
  // Save HTML report
  const htmlPath = path.join(CONFIG.outputDir, 'accessibility-report.html');
  await fs.writeFile(htmlPath, htmlReport);
  
  // Save JSON summary
  const summaryPath = path.join(CONFIG.outputDir, 'accessibility-summary.json');
  await fs.writeFile(summaryPath, JSON.stringify(summary, null, 2));
  
  log(`📊 HTML report saved to ${htmlPath}`, 'green');
  log(`📊 JSON summary saved to ${summaryPath}`, 'green');
  
  return summary;
}

/**
 * Main execution function
 */
async function main() {
  try {
    log('🌱 Starting Digital Greenhouse Accessibility Audit...', 'green');
    
    // Ensure output directory exists
    await ensureOutputDir();
    
    // Wait for server to be ready
    log('⏳ Waiting for server to be ready...', 'yellow');
    await waitForServer(CONFIG.baseUrl);
    log(`✅ Server is ready at ${CONFIG.baseUrl}`, 'green');
    
    // Run accessibility tests
    const [axeResults, pa11yResults] = await Promise.all([
      runAxeTests(),
      runPa11yTests()
    ]);
    
    // Generate comprehensive report
    const summary = await generateReport(axeResults, pa11yResults);
    
    // Final summary
    log('\n📋 Accessibility Audit Complete!', 'green');
    log(`📊 Total Axe violations: ${summary.axe.totalViolations}`, 
         summary.axe.totalViolations === 0 ? 'green' : 'red');
    log(`📊 Total Pa11y issues: ${summary.pa11y.totalIssues}`, 
         summary.pa11y.totalIssues === 0 ? 'green' : 'red');
    
    if (summary.axe.totalViolations === 0 && summary.pa11y.totalIssues === 0) {
      log('🎉 Congratulations! No accessibility issues found!', 'green');
      process.exit(0);
    } else {
      log('⚠️  Please review and fix the accessibility issues found.', 'yellow');
      log(`📄 Detailed report: ${path.join(CONFIG.outputDir, 'accessibility-report.html')}`, 'cyan');
      
      // Exit with error code if there are violations
      if (process.env.CI && (summary.axe.totalViolations > 0 || summary.pa11y.totalIssues > 0)) {
        process.exit(1);
      }
    }
    
  } catch (error) {
    log(`❌ Accessibility audit failed: ${error.message}`, 'red');
    console.error(error);
    process.exit(1);
  }
}

// Run the audit if this script is executed directly
if (require.main === module) {
  main();
}

module.exports = {
  runAxeTests,
  runPa11yTests,
  generateReport,
  CONFIG
};