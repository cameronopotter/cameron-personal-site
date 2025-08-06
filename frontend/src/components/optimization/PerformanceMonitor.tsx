import React, { useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { useGardenStore } from '@/stores/gardenStore'

export const PerformanceMonitor: React.FC = () => {
  const frameCount = useRef(0)
  const lastTime = useRef(performance.now())
  const renderTimes = useRef<number[]>([])
  
  const { gl, scene, camera } = useThree()
  const { updatePerformanceMetrics, enableOptimizedMode, performance: performanceSettings } = useGardenStore()

  useFrame((state, delta) => {
    frameCount.current++
    const currentTime = performance.now()
    const frameTime = currentTime - lastTime.current
    
    renderTimes.current.push(frameTime)
    
    // Keep only last 60 frames
    if (renderTimes.current.length > 60) {
      renderTimes.current.shift()
    }
    
    // Update performance metrics every 30 frames
    if (frameCount.current % 30 === 0) {
      const avgFrameTime = renderTimes.current.reduce((a, b) => a + b, 0) / renderTimes.current.length
      const fps = Math.round(1000 / avgFrameTime)
      
      // Get WebGL context info
      const info = gl.info
      const memoryInfo = (performance as any).memory
      
      const metrics = {
        fps,
        renderTime: avgFrameTime,
        memoryUsage: memoryInfo ? Math.round(memoryInfo.usedJSHeapSize / 1024 / 1024) : 0,
        geometryCount: info.geometries,
        materialCount: info.textures,
        drawCalls: info.render.calls,
        triangles: info.render.triangles
      }
      
      updatePerformanceMetrics(metrics)
      
      // Auto-optimize if performance drops
      if (fps < 25 && !performanceSettings.isOptimizedMode) {
        enableOptimizedMode()
        console.warn('Performance degraded, enabling optimized mode')
      }
      
      // Log detailed performance info in development
      if (import.meta.env.DEV && frameCount.current % 300 === 0) {
        console.log('Garden Performance Metrics:', {
          ...metrics,
          sceneChildren: scene.children.length,
          cameraPosition: camera.position,
          glInfo: {
            renderer: gl.capabilities.getMaxAnisotropy(),
            maxTextures: gl.capabilities.maxTextures,
            maxVertexTextures: gl.capabilities.maxVertexTextures,
            precision: gl.capabilities.precision
          }
        })
      }
    }
    
    lastTime.current = currentTime
  })

  // This component doesn't render anything visible
  return null
}