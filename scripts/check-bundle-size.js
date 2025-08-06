#!/usr/bin/env node

/**
 * Bundle Size Checker for Digital Greenhouse
 * Ensures production builds stay within performance budgets
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const gzip = require('zlib').gzip;

const gzipAsync = promisify(gzip);

// Performance budgets (in bytes)
const PERFORMANCE_BUDGETS = {
  // Main JavaScript bundle
  'index': {
    raw: 500 * 1024,      // 500KB raw
    gzip: 150 * 1024      // 150KB gzipped
  },
  // Vendor chunks
  'react-vendor': {
    raw: 200 * 1024,      // 200KB raw
    gzip: 70 * 1024       // 70KB gzipped
  },
  'three-vendor': {
    raw: 800 * 1024,      // 800KB raw (Three.js is large)
    gzip: 250 * 1024      // 250KB gzipped
  },
  'ui-vendor': {
    raw: 300 * 1024,      // 300KB raw
    gzip: 90 * 1024       // 90KB gzipped
  },
  // Total budget
  'total': {
    raw: 2 * 1024 * 1024,   // 2MB total raw
    gzip: 600 * 1024        // 600KB total gzipped
  }
};

/**
 * Get file size in bytes
 */
function getFileSize(filePath) {
  try {
    return fs.statSync(filePath).size;
  } catch (error) {
    return 0;
  }
}

/**
 * Get gzipped size of file
 */
async function getGzipSize(filePath) {
  try {
    const fileContent = fs.readFileSync(filePath);
    const gzipped = await gzipAsync(fileContent);
    return gzipped.length;
  } catch (error) {
    return 0;
  }
}

/**
 * Format bytes to human readable string
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Find JavaScript files in dist directory
 */
function findJSFiles(distDir) {
  const jsFiles = [];
  
  function searchDir(dir) {
    const items = fs.readdirSync(dir);
    
    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        searchDir(fullPath);
      } else if (item.endsWith('.js') && !item.endsWith('.map')) {
        jsFiles.push(fullPath);
      }
    }
  }
  
  if (fs.existsSync(distDir)) {
    searchDir(distDir);
  }
  
  return jsFiles;
}

/**
 * Categorize bundle files
 */
function categorizeBundles(jsFiles) {
  const bundles = {
    'index': [],
    'react-vendor': [],
    'three-vendor': [],
    'ui-vendor': [],
    'animation-vendor': [],
    'other': []
  };
  
  for (const file of jsFiles) {
    const fileName = path.basename(file).toLowerCase();
    
    if (fileName.includes('index') || fileName.includes('main')) {
      bundles.index.push(file);
    } else if (fileName.includes('react-vendor')) {
      bundles['react-vendor'].push(file);
    } else if (fileName.includes('three-vendor')) {
      bundles['three-vendor'].push(file);
    } else if (fileName.includes('ui-vendor')) {
      bundles['ui-vendor'].push(file);
    } else if (fileName.includes('animation-vendor')) {
      bundles['animation-vendor'].push(file);
    } else {
      bundles.other.push(file);
    }
  }
  
  return bundles;
}

/**
 * Check bundle against performance budget
 */
function checkBudget(bundleName, rawSize, gzipSize, budget) {
  const results = {
    name: bundleName,
    rawSize,
    gzipSize,
    rawBudget: budget?.raw || 0,
    gzipBudget: budget?.gzip || 0,
    rawOverBudget: budget?.raw ? rawSize > budget.raw : false,
    gzipOverBudget: budget?.gzip ? gzipSize > budget.gzip : false
  };
  
  results.overBudget = results.rawOverBudget || results.gzipOverBudget;
  
  return results;
}

/**
 * Generate bundle size report
 */
async function generateBundleSizeReport() {
  console.log('🔍 Analyzing bundle sizes...\n');
  
  const distDir = path.join(__dirname, '../frontend/dist');
  const jsFiles = findJSFiles(distDir);
  
  if (jsFiles.length === 0) {
    console.error('❌ No JavaScript files found in dist directory');
    console.log('   Make sure you run "npm run build" first');
    process.exit(1);
  }
  
  const bundles = categorizeBundles(jsFiles);
  const results = [];
  let totalRawSize = 0;
  let totalGzipSize = 0;
  let hasOverBudget = false;
  
  // Check each bundle category
  for (const [bundleName, files] of Object.entries(bundles)) {
    if (files.length === 0) continue;
    
    let bundleRawSize = 0;
    let bundleGzipSize = 0;
    
    // Calculate total size for this bundle category
    for (const file of files) {
      const rawSize = getFileSize(file);
      const gzipSize = await getGzipSize(file);
      
      bundleRawSize += rawSize;
      bundleGzipSize += gzipSize;
      totalRawSize += rawSize;
      totalGzipSize += gzipSize;
    }
    
    // Check against budget
    const budget = PERFORMANCE_BUDGETS[bundleName];
    const result = checkBudget(bundleName, bundleRawSize, bundleGzipSize, budget);
    results.push(result);
    
    if (result.overBudget) {
      hasOverBudget = true;
    }
  }
  
  // Check total budget
  const totalBudget = PERFORMANCE_BUDGETS.total;
  const totalResult = checkBudget('total', totalRawSize, totalGzipSize, totalBudget);
  results.push(totalResult);
  
  if (totalResult.overBudget) {
    hasOverBudget = true;
  }
  
  // Display results
  console.log('📦 Bundle Size Report\n');
  console.log('Bundle Name          Raw Size    Gzipped    Budget (Raw/Gzip)    Status');
  console.log('───────────────────────────────────────────────────────────────────────');
  
  for (const result of results) {
    const name = result.name.padEnd(18);
    const rawSize = formatBytes(result.rawSize).padStart(10);
    const gzipSize = formatBytes(result.gzipSize).padStart(10);
    
    let budgetInfo = '';
    if (result.rawBudget > 0) {
      budgetInfo = `${formatBytes(result.rawBudget)}/${formatBytes(result.gzipBudget)}`;
    }
    budgetInfo = budgetInfo.padEnd(18);
    
    let status = '✅ OK';
    if (result.overBudget) {
      if (result.rawOverBudget && result.gzipOverBudget) {
        status = '❌ OVER (Raw + Gzip)';
      } else if (result.rawOverBudget) {
        status = '⚠️  OVER (Raw)';
      } else {
        status = '⚠️  OVER (Gzip)';
      }
    }
    
    console.log(`${name} ${rawSize} ${gzipSize} ${budgetInfo} ${status}`);
  }
  
  // Summary
  console.log('\n📊 Summary:');
  console.log(`Total Raw Size: ${formatBytes(totalRawSize)}`);
  console.log(`Total Gzipped: ${formatBytes(totalGzipSize)}`);
  console.log(`Compression Ratio: ${((1 - totalGzipSize / totalRawSize) * 100).toFixed(1)}%`);
  
  if (hasOverBudget) {
    console.log('\n❌ Bundle size check FAILED!');
    console.log('\n💡 Optimization suggestions:');
    console.log('   • Enable tree-shaking for unused code');
    console.log('   • Use dynamic imports for code splitting');
    console.log('   • Optimize Three.js imports (use selective imports)');
    console.log('   • Consider lazy loading non-critical features');
    console.log('   • Use webpack-bundle-analyzer to identify large dependencies');
    
    process.exit(1);
  } else {
    console.log('\n✅ All bundles are within performance budgets!');
    
    // Show optimization opportunities
    const compressionRatio = totalGzipSize / totalRawSize;
    if (compressionRatio > 0.4) {
      console.log('\n💡 Tip: Consider additional minification for better compression');
    }
    
    process.exit(0);
  }
}

/**
 * Compare with previous build (if available)
 */
async function comparePreviousBuild() {
  const reportPath = path.join(__dirname, '../bundle-size-report.json');
  const currentReport = {
    timestamp: new Date().toISOString(),
    totalRawSize: 0,
    totalGzipSize: 0,
    bundles: {}
  };
  
  // Generate current report data
  const distDir = path.join(__dirname, '../frontend/dist');
  const jsFiles = findJSFiles(distDir);
  const bundles = categorizeBundles(jsFiles);
  
  for (const [bundleName, files] of Object.entries(bundles)) {
    if (files.length === 0) continue;
    
    let bundleRawSize = 0;
    let bundleGzipSize = 0;
    
    for (const file of files) {
      const rawSize = getFileSize(file);
      const gzipSize = await getGzipSize(file);
      
      bundleRawSize += rawSize;
      bundleGzipSize += gzipSize;
      currentReport.totalRawSize += rawSize;
      currentReport.totalGzipSize += gzipSize;
    }
    
    currentReport.bundles[bundleName] = {
      rawSize: bundleRawSize,
      gzipSize: bundleGzipSize
    };
  }
  
  // Compare with previous if available
  if (fs.existsSync(reportPath)) {
    try {
      const previousReport = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
      
      console.log('\n📈 Size Comparison (vs previous build):');
      
      const rawDiff = currentReport.totalRawSize - previousReport.totalRawSize;
      const gzipDiff = currentReport.totalGzipSize - previousReport.totalGzipSize;
      
      const rawDiffStr = rawDiff >= 0 ? `+${formatBytes(rawDiff)}` : formatBytes(rawDiff);
      const gzipDiffStr = gzipDiff >= 0 ? `+${formatBytes(gzipDiff)}` : formatBytes(gzipDiff);
      
      console.log(`Raw Size Change: ${rawDiffStr}`);
      console.log(`Gzipped Change: ${gzipDiffStr}`);
      
      // Warn about significant increases
      const rawIncrease = rawDiff / previousReport.totalRawSize;
      const gzipIncrease = gzipDiff / previousReport.totalGzipSize;
      
      if (rawIncrease > 0.1 || gzipIncrease > 0.1) {
        console.log('\n⚠️  Bundle size increased significantly!');
      } else if (rawDiff < 0 && gzipDiff < 0) {
        console.log('\n🎉 Bundle size decreased!');
      }
      
    } catch (error) {
      console.warn('Could not compare with previous build:', error.message);
    }
  }
  
  // Save current report
  fs.writeFileSync(reportPath, JSON.stringify(currentReport, null, 2));
}

// Run the bundle size check
async function main() {
  try {
    await generateBundleSizeReport();
    await comparePreviousBuild();
  } catch (error) {
    console.error('❌ Bundle size check failed:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  generateBundleSizeReport,
  comparePreviousBuild,
  formatBytes,
  getFileSize,
  getGzipSize
};