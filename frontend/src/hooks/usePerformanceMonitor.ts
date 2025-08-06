import { useEffect, useState, useRef, useCallback } from 'react'
import { useGardenStore } from '@/stores/gardenStore'

interface PerformanceMetrics {
  fps: number
  renderTime: number
  memoryUsage: number
  isOptimizing: boolean
}

export const usePerformanceMonitor = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    fps: 60,
    renderTime: 16.67,
    memoryUsage: 0,
    isOptimizing: false
  })
  
  const frameCountRef = useRef(0)
  const lastTimeRef = useRef(performance.now())
  const renderTimesRef = useRef<number[]>([])
  const fpsHistoryRef = useRef<number[]>([])
  const animationFrameRef = useRef<number>()
  
  const { updatePerformanceMetrics, enableOptimizedMode, disableOptimizedMode } = useGardenStore()
  
  const measureFrame = useCallback(() => {
    const now = performance.now()
    const delta = now - lastTimeRef.current
    const fps = 1000 / delta
    
    frameCountRef.current += 1
    renderTimesRef.current.push(delta)
    fpsHistoryRef.current.push(fps)
    
    // Keep only recent measurements (last 60 frames)
    if (renderTimesRef.current.length > 60) {
      renderTimesRef.current.shift()
      fpsHistoryRef.current.shift()
    }
    
    // Update metrics every 30 frames
    if (frameCountRef.current % 30 === 0) {
      const avgRenderTime = renderTimesRef.current.reduce((a, b) => a + b, 0) / renderTimesRef.current.length
      const avgFps = fpsHistoryRef.current.reduce((a, b) => a + b, 0) / fpsHistoryRef.current.length
      
      // Get memory usage if available
      const memoryUsage = (performance as any).memory?.usedJSHeapSize || 0
      
      // Determine if we should optimize
      const shouldOptimize = avgFps < 30 || avgRenderTime > 33.33
      
      const newMetrics = {
        fps: Math.round(avgFps),
        renderTime: Math.round(avgRenderTime * 100) / 100,
        memoryUsage: Math.round(memoryUsage / 1024 / 1024), // Convert to MB
        isOptimizing: shouldOptimize
      }
      
      setMetrics(newMetrics)
      updatePerformanceMetrics(newMetrics)
      
      // Auto-optimize if performance is poor
      if (shouldOptimize && !useGardenStore.getState().performance.isOptimizedMode) {
        enableOptimizedMode()
      } else if (!shouldOptimize && useGardenStore.getState().performance.isOptimizedMode) {
        // Wait a bit before disabling optimization to avoid thrashing
        setTimeout(() => {
          if (fpsHistoryRef.current.slice(-10).every(f => f > 45)) {
            disableOptimizedMode()
          }
        }, 5000)
      }
    }
    
    lastTimeRef.current = now
    animationFrameRef.current = requestAnimationFrame(measureFrame)
  }, [updatePerformanceMetrics, enableOptimizedMode, disableOptimizedMode])
  
  // Start monitoring
  useEffect(() => {
    animationFrameRef.current = requestAnimationFrame(measureFrame)
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [measureFrame])
  
  // Monitor memory usage periodically
  useEffect(() => {
    const memoryInterval = setInterval(() => {
      if ((performance as any).memory) {
        const memoryInfo = (performance as any).memory
        const memoryUsage = Math.round(memoryInfo.usedJSHeapSize / 1024 / 1024)
        
        setMetrics(prev => ({ ...prev, memoryUsage }))
        
        // Warn if memory usage is high (over 100MB)
        if (memoryUsage > 100) {
          useGardenStore.getState().showNotification({
            type: 'warning',
            message: 'High memory usage detected. Consider refreshing the page.',
            duration: 5000,
            persistent: false
          })
        }
      }
    }, 10000) // Check every 10 seconds
    
    return () => clearInterval(memoryInterval)
  }, [])
  
  // DevTools integration for performance monitoring
  useEffect(() => {
    if (import.meta.env.DEV) {
      // Log performance metrics to console in development
      const logInterval = setInterval(() => {
        console.log('Garden Performance:', metrics)
      }, 5000)
      
      return () => clearInterval(logInterval)
    }
  }, [metrics])
  
  return metrics
}