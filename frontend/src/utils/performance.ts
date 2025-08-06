/**
 * Performance monitoring and optimization utilities for Digital Greenhouse
 * Comprehensive performance tracking, metrics collection, and optimization suggestions
 */

// Performance Metrics Types
export interface PerformanceMetrics {
  fps: number;
  renderTime: number;
  memoryUsage: number;
  drawCalls: number;
  triangles: number;
  shaderSwitches: number;
  textureMemory: number;
  geometryMemory: number;
  networkLatency: number;
  bundleLoadTime: number;
  interactionLatency: number;
}

export interface FrameTimingMetrics {
  frameStart: number;
  renderStart: number;
  renderEnd: number;
  frameEnd: number;
  frameDuration: number;
  renderDuration: number;
  scriptDuration: number;
  idleDuration: number;
}

export interface ResourceMetrics {
  name: string;
  type: 'texture' | 'geometry' | 'material' | 'shader' | 'sound';
  size: number;
  loadTime: number;
  lastUsed: number;
  usageCount: number;
  priority: 'critical' | 'high' | 'medium' | 'low';
}

export interface OptimizationSuggestion {
  type: 'performance' | 'memory' | 'network' | 'rendering';
  severity: 'critical' | 'warning' | 'info';
  message: string;
  impact: 'high' | 'medium' | 'low';
  solution: string;
  implementation?: () => void;
}

/**
 * Performance Monitor Class
 * Comprehensive performance tracking and analysis
 */
export class PerformanceMonitor {
  private metrics: PerformanceMetrics = {
    fps: 0,
    renderTime: 0,
    memoryUsage: 0,
    drawCalls: 0,
    triangles: 0,
    shaderSwitches: 0,
    textureMemory: 0,
    geometryMemory: 0,
    networkLatency: 0,
    bundleLoadTime: 0,
    interactionLatency: 0
  };

  private frameTimes: number[] = [];
  private renderTimes: number[] = [];
  private resourceUsage: Map<string, ResourceMetrics> = new Map();
  private isMonitoring = false;
  private rafId?: number;
  private lastFrameTime = 0;
  private frameCount = 0;
  private startTime = performance.now();
  
  // Performance budgets
  private readonly PERFORMANCE_BUDGETS = {
    targetFPS: 60,
    maxFrameTime: 16.67, // 60fps = 16.67ms per frame
    maxRenderTime: 12,   // Leave 4ms for other work
    maxMemoryMB: 512,    // 512MB memory budget
    maxDrawCalls: 100,   // Aim for <100 draw calls per frame
    maxTriangles: 500000 // 500k triangles max
  };

  constructor() {
    this.initializePerformanceAPI();
  }

  /**
   * Initialize performance monitoring APIs
   */
  private initializePerformanceAPI(): void {
    // Enhanced performance.mark/measure
    this.patchPerformanceAPI();
    
    // Memory monitoring
    this.initMemoryMonitoring();
    
    // Network monitoring
    this.initNetworkMonitoring();
  }

  /**
   * Patch performance API for better tracking
   */
  private patchPerformanceAPI(): void {
    const originalMark = performance.mark.bind(performance);
    const originalMeasure = performance.measure.bind(performance);

    performance.mark = (markName: string, markOptions?: any) => {
      const result = originalMark(markName, markOptions);
      this.trackCustomMetric('mark', markName, performance.now());
      return result;
    };

    performance.measure = (measureName: string, startMark?: string, endMark?: string) => {
      const result = originalMeasure(measureName, startMark, endMark);
      const entries = performance.getEntriesByName(measureName, 'measure');
      if (entries.length > 0) {
        const latestEntry = entries[entries.length - 1];
        this.trackCustomMetric('measure', measureName, latestEntry.duration);
      }
      return result;
    };
  }

  /**
   * Initialize memory monitoring
   */
  private initMemoryMonitoring(): void {
    if ('memory' in performance) {
      setInterval(() => {
        const memory = (performance as any).memory;
        this.metrics.memoryUsage = memory.usedJSHeapSize;
        
        // Check for memory leaks
        this.detectMemoryLeaks();
      }, 5000); // Check every 5 seconds
    }
  }

  /**
   * Initialize network monitoring
   */
  private initNetworkMonitoring(): void {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      
      // Monitor network quality
      const updateNetworkInfo = () => {
        this.trackNetworkQuality(connection.effectiveType, connection.downlink);
      };
      
      connection.addEventListener('change', updateNetworkInfo);
      updateNetworkInfo();
    }
  }

  /**
   * Start performance monitoring
   */
  public startMonitoring(): void {
    if (this.isMonitoring) return;
    
    this.isMonitoring = true;
    this.startTime = performance.now();
    this.lastFrameTime = this.startTime;
    this.frameCount = 0;
    
    this.monitorFrame();
  }

  /**
   * Stop performance monitoring
   */
  public stopMonitoring(): void {
    this.isMonitoring = false;
    
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = undefined;
    }
  }

  /**
   * Monitor each frame for performance metrics
   */
  private monitorFrame(): void {
    if (!this.isMonitoring) return;

    const frameStart = performance.now();
    
    // Calculate FPS
    const frameDelta = frameStart - this.lastFrameTime;
    this.frameTimes.push(frameDelta);
    
    // Keep only last 60 frames for rolling average
    if (this.frameTimes.length > 60) {
      this.frameTimes.shift();
    }
    
    // Calculate rolling FPS
    const avgFrameTime = this.frameTimes.reduce((sum, time) => sum + time, 0) / this.frameTimes.length;
    this.metrics.fps = 1000 / avgFrameTime;
    
    this.lastFrameTime = frameStart;
    this.frameCount++;
    
    // Schedule next frame
    this.rafId = requestAnimationFrame(() => this.monitorFrame());
  }

  /**
   * Track custom performance metric
   */
  public trackCustomMetric(category: string, name: string, value: number): void {
    const metricName = `${category}:${name}`;
    performance.mark(`${metricName}-${value}`);
  }

  /**
   * Track render performance
   */
  public trackRenderPerformance(renderTime: number, drawCalls: number, triangles: number): void {
    this.metrics.renderTime = renderTime;
    this.metrics.drawCalls = drawCalls;
    this.metrics.triangles = triangles;
    
    this.renderTimes.push(renderTime);
    if (this.renderTimes.length > 60) {
      this.renderTimes.shift();
    }
    
    // Check render performance budgets
    this.checkRenderBudgets();
  }

  /**
   * Track resource usage
   */
  public trackResourceUsage(name: string, type: ResourceMetrics['type'], size: number, loadTime?: number): void {
    const existing = this.resourceUsage.get(name);
    const now = performance.now();
    
    if (existing) {
      existing.lastUsed = now;
      existing.usageCount++;
    } else {
      this.resourceUsage.set(name, {
        name,
        type,
        size,
        loadTime: loadTime || 0,
        lastUsed: now,
        usageCount: 1,
        priority: this.calculateResourcePriority(type, size)
      });
    }
    
    this.updateMemoryUsage();
  }

  /**
   * Calculate resource priority based on type and size
   */
  private calculateResourcePriority(type: ResourceMetrics['type'], size: number): ResourceMetrics['priority'] {
    if (type === 'shader' || (type === 'texture' && size < 1024 * 1024)) {
      return 'critical';
    }
    if (type === 'geometry' || size < 5 * 1024 * 1024) {
      return 'high';
    }
    if (size < 20 * 1024 * 1024) {
      return 'medium';
    }
    return 'low';
  }

  /**
   * Update memory usage calculations
   */
  private updateMemoryUsage(): void {
    let textureMemory = 0;
    let geometryMemory = 0;
    
    for (const resource of this.resourceUsage.values()) {
      if (resource.type === 'texture') {
        textureMemory += resource.size;
      } else if (resource.type === 'geometry') {
        geometryMemory += resource.size;
      }
    }
    
    this.metrics.textureMemory = textureMemory;
    this.metrics.geometryMemory = geometryMemory;
  }

  /**
   * Track interaction latency
   */
  public trackInteractionLatency(interactionType: string, latency: number): void {
    this.metrics.interactionLatency = latency;
    performance.mark(`interaction-${interactionType}-${latency}`);
    
    // Log slow interactions
    if (latency > 100) {
      console.warn(`Slow interaction detected: ${interactionType} took ${latency}ms`);
    }
  }

  /**
   * Track network latency
   */
  private trackNetworkQuality(effectiveType: string, downlink: number): void {
    this.metrics.networkLatency = this.estimateLatencyFromConnection(effectiveType);
    
    // Adjust performance based on network
    this.adjustForNetworkConditions(effectiveType, downlink);
  }

  /**
   * Estimate network latency from connection type
   */
  private estimateLatencyFromConnection(effectiveType: string): number {
    const latencyMap: Record<string, number> = {
      'slow-2g': 2000,
      '2g': 1400,
      '3g': 400,
      '4g': 100,
      '5g': 20
    };
    
    return latencyMap[effectiveType] || 100;
  }

  /**
   * Adjust performance settings based on network conditions
   */
  private adjustForNetworkConditions(effectiveType: string, downlink: number): void {
    if (effectiveType === 'slow-2g' || effectiveType === '2g' || downlink < 1) {
      // Suggest low quality mode
      this.suggestOptimization({
        type: 'network',
        severity: 'warning',
        message: 'Slow network detected',
        impact: 'medium',
        solution: 'Enable low-bandwidth mode to reduce data usage',
        implementation: () => this.enableLowBandwidthMode()
      });
    }
  }

  /**
   * Enable low bandwidth mode
   */
  private enableLowBandwidthMode(): void {
    // This would integrate with your settings system
    console.log('Enabling low bandwidth mode...');
    
    // Reduce texture quality, disable high-poly models, etc.
    document.dispatchEvent(new CustomEvent('performance:enableLowBandwidth', {
      detail: { reason: 'network_conditions' }
    }));
  }

  /**
   * Check render performance budgets
   */
  private checkRenderBudgets(): void {
    const suggestions: OptimizationSuggestion[] = [];
    
    // FPS check
    if (this.metrics.fps < this.PERFORMANCE_BUDGETS.targetFPS * 0.8) {
      suggestions.push({
        type: 'performance',
        severity: 'warning',
        message: `Low FPS detected: ${this.metrics.fps.toFixed(1)} (target: ${this.PERFORMANCE_BUDGETS.targetFPS})`,
        impact: 'high',
        solution: 'Reduce scene complexity or enable performance mode'
      });
    }
    
    // Render time check
    if (this.metrics.renderTime > this.PERFORMANCE_BUDGETS.maxRenderTime) {
      suggestions.push({
        type: 'rendering',
        severity: 'warning',
        message: `Render time too high: ${this.metrics.renderTime.toFixed(2)}ms (target: <${this.PERFORMANCE_BUDGETS.maxRenderTime}ms)`,
        impact: 'high',
        solution: 'Implement LOD system or reduce draw calls'
      });
    }
    
    // Draw calls check
    if (this.metrics.drawCalls > this.PERFORMANCE_BUDGETS.maxDrawCalls) {
      suggestions.push({
        type: 'rendering',
        severity: 'critical',
        message: `Too many draw calls: ${this.metrics.drawCalls} (target: <${this.PERFORMANCE_BUDGETS.maxDrawCalls})`,
        impact: 'high',
        solution: 'Implement instancing or geometry batching'
      });
    }
    
    // Memory check
    const memoryMB = this.metrics.memoryUsage / (1024 * 1024);
    if (memoryMB > this.PERFORMANCE_BUDGETS.maxMemoryMB) {
      suggestions.push({
        type: 'memory',
        severity: 'critical',
        message: `Memory usage too high: ${memoryMB.toFixed(1)}MB (target: <${this.PERFORMANCE_BUDGETS.maxMemoryMB}MB)`,
        impact: 'high',
        solution: 'Dispose unused resources or implement resource pooling'
      });
    }
    
    // Notify about suggestions
    suggestions.forEach(suggestion => this.suggestOptimization(suggestion));
  }

  /**
   * Detect memory leaks
   */
  private detectMemoryLeaks(): void {
    const memoryMB = this.metrics.memoryUsage / (1024 * 1024);
    const runtimeMinutes = (performance.now() - this.startTime) / (1000 * 60);
    
    // Check for steady memory increase
    if (runtimeMinutes > 5 && memoryMB > 200) {
      const memoryGrowthRate = memoryMB / runtimeMinutes; // MB per minute
      
      if (memoryGrowthRate > 10) { // Growing by >10MB per minute
        this.suggestOptimization({
          type: 'memory',
          severity: 'critical',
          message: `Potential memory leak detected (${memoryGrowthRate.toFixed(1)}MB/min growth)`,
          impact: 'high',
          solution: 'Check for undisposed Three.js objects or event listeners'
        });
      }
    }
  }

  /**
   * Suggest optimization
   */
  private suggestOptimization(suggestion: OptimizationSuggestion): void {
    // Emit custom event for UI to handle
    document.dispatchEvent(new CustomEvent('performance:suggestion', {
      detail: suggestion
    }));
    
    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      const emoji = suggestion.severity === 'critical' ? '🚨' : suggestion.severity === 'warning' ? '⚠️' : 'ℹ️';
      console.warn(`${emoji} Performance ${suggestion.type}:`, suggestion.message);
      console.log(`💡 Solution: ${suggestion.solution}`);
    }
  }

  /**
   * Get performance report
   */
  public getPerformanceReport(): {
    metrics: PerformanceMetrics;
    frameTimings: number[];
    resourceUsage: ResourceMetrics[];
    runtime: number;
    suggestions: OptimizationSuggestion[];
  } {
    const suggestions = this.generateOptimizationSuggestions();
    
    return {
      metrics: { ...this.metrics },
      frameTimings: [...this.frameTimes],
      resourceUsage: Array.from(this.resourceUsage.values()),
      runtime: performance.now() - this.startTime,
      suggestions
    };
  }

  /**
   * Generate optimization suggestions based on current metrics
   */
  private generateOptimizationSuggestions(): OptimizationSuggestion[] {
    const suggestions: OptimizationSuggestion[] = [];
    
    // Analyze resource usage patterns
    const unusedResources = Array.from(this.resourceUsage.values())
      .filter(resource => performance.now() - resource.lastUsed > 60000); // Unused for 1 minute
    
    if (unusedResources.length > 10) {
      suggestions.push({
        type: 'memory',
        severity: 'warning',
        message: `${unusedResources.length} resources haven't been used recently`,
        impact: 'medium',
        solution: 'Implement resource garbage collection',
        implementation: () => this.cleanupUnusedResources()
      });
    }
    
    // Check texture memory usage
    const textureMB = this.metrics.textureMemory / (1024 * 1024);
    if (textureMB > 256) {
      suggestions.push({
        type: 'memory',
        severity: 'warning',
        message: `High texture memory usage: ${textureMB.toFixed(1)}MB`,
        impact: 'medium',
        solution: 'Compress textures or reduce resolution'
      });
    }
    
    return suggestions;
  }

  /**
   * Cleanup unused resources
   */
  private cleanupUnusedResources(): void {
    const cutoffTime = performance.now() - 60000; // 1 minute ago
    let cleanedCount = 0;
    
    for (const [name, resource] of this.resourceUsage.entries()) {
      if (resource.lastUsed < cutoffTime && resource.priority === 'low') {
        this.resourceUsage.delete(name);
        cleanedCount++;
      }
    }
    
    console.log(`Cleaned up ${cleanedCount} unused resources`);
    this.updateMemoryUsage();
  }

  /**
   * Export performance data for analysis
   */
  public exportPerformanceData(): string {
    const report = this.getPerformanceReport();
    const exportData = {
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      ...report
    };
    
    return JSON.stringify(exportData, null, 2);
  }

  /**
   * Get current metrics
   */
  public getCurrentMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  /**
   * Reset all metrics
   */
  public reset(): void {
    this.metrics = {
      fps: 0,
      renderTime: 0,
      memoryUsage: 0,
      drawCalls: 0,
      triangles: 0,
      shaderSwitches: 0,
      textureMemory: 0,
      geometryMemory: 0,
      networkLatency: 0,
      bundleLoadTime: 0,
      interactionLatency: 0
    };
    
    this.frameTimes = [];
    this.renderTimes = [];
    this.resourceUsage.clear();
    this.frameCount = 0;
    this.startTime = performance.now();
  }
}

// Singleton instance
export const performanceMonitor = new PerformanceMonitor();

/**
 * React hook for performance monitoring
 */
export function usePerformanceMonitor() {
  return {
    startMonitoring: () => performanceMonitor.startMonitoring(),
    stopMonitoring: () => performanceMonitor.stopMonitoring(),
    getCurrentMetrics: () => performanceMonitor.getCurrentMetrics(),
    getPerformanceReport: () => performanceMonitor.getPerformanceReport(),
    trackRenderPerformance: (renderTime: number, drawCalls: number, triangles: number) =>
      performanceMonitor.trackRenderPerformance(renderTime, drawCalls, triangles),
    trackResourceUsage: (name: string, type: ResourceMetrics['type'], size: number, loadTime?: number) =>
      performanceMonitor.trackResourceUsage(name, type, size, loadTime),
    trackInteractionLatency: (interactionType: string, latency: number) =>
      performanceMonitor.trackInteractionLatency(interactionType, latency),
    exportData: () => performanceMonitor.exportPerformanceData(),
    reset: () => performanceMonitor.reset()
  };
}