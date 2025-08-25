interface DeviceInfo {
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
  screenSize: 'small' | 'medium' | 'large' | 'xl'
  orientation: 'portrait' | 'landscape'
  hasTouch: boolean
  performanceLevel: 'low' | 'medium' | 'high'
  maxTextureSize: number
  devicePixelRatio: number
  memoryLevel: 'low' | 'medium' | 'high'
  connectionType: string
}

interface OptimizationSettings {
  complexityLevel: 1 | 2 | 3 | 4
  particlesEnabled: boolean
  shadowsEnabled: boolean
  antialiasing: boolean
  maxParticleCount: number
  lodDistance: number
  autoRotateSpeed: number
  renderScale: number
  maxFPS: number
  weatherEnabled: boolean
  postProcessingEnabled: boolean
}

class MobileOptimizationService {
  private deviceInfo: DeviceInfo
  private resizeObserver?: ResizeObserver
  private performanceObserver?: PerformanceObserver
  private listeners: Array<(settings: OptimizationSettings) => void> = []
  
  constructor() {
    this.deviceInfo = this.analyzeDevice()
    this.setupPerformanceMonitoring()
    this.setupResizeObserver()
  }

  private analyzeDevice(): DeviceInfo {
    const userAgent = navigator.userAgent.toLowerCase()
    const width = window.innerWidth
    const height = window.innerHeight
    
    // Device type detection
    const isMobile = /mobile|android|iphone|ipod|blackberry|iemobile/.test(userAgent) || width < 768
    const isTablet = /tablet|ipad/.test(userAgent) || (width >= 768 && width < 1024)
    const isDesktop = !isMobile && !isTablet
    
    // Screen size classification
    let screenSize: DeviceInfo['screenSize']
    if (width < 576) screenSize = 'small'
    else if (width < 768) screenSize = 'medium' 
    else if (width < 1200) screenSize = 'large'
    else screenSize = 'xl'
    
    // Performance detection
    const canvas = document.createElement('canvas')
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl')
    const maxTextureSize = gl ? gl.getParameter(gl.MAX_TEXTURE_SIZE) : 1024
    
    // Memory detection
    const deviceMemory = (navigator as any).deviceMemory || 4
    let memoryLevel: DeviceInfo['memoryLevel']
    if (deviceMemory <= 2) memoryLevel = 'low'
    else if (deviceMemory <= 4) memoryLevel = 'medium'
    else memoryLevel = 'high'
    
    // Performance level estimation
    let performanceLevel: DeviceInfo['performanceLevel']
    if (isMobile && deviceMemory <= 2) performanceLevel = 'low'
    else if (isMobile && deviceMemory <= 4) performanceLevel = 'medium'
    else if (isDesktop && deviceMemory >= 8) performanceLevel = 'high'
    else performanceLevel = 'medium'
    
    // Connection type
    const connection = (navigator as any).connection
    const connectionType = connection?.effectiveType || 'unknown'
    
    return {
      isMobile,
      isTablet,
      isDesktop,
      screenSize,
      orientation: height > width ? 'portrait' : 'landscape',
      hasTouch: 'ontouchstart' in window,
      performanceLevel,
      maxTextureSize,
      devicePixelRatio: window.devicePixelRatio || 1,
      memoryLevel,
      connectionType
    }
  }

  private getOptimalSettings(): OptimizationSettings {
    const { performanceLevel, isMobile, screenSize, memoryLevel, connectionType } = this.deviceInfo
    
    // Base settings for different performance levels
    const baseSettings = {
      low: {
        complexityLevel: 1 as const,
        particlesEnabled: false,
        shadowsEnabled: false,
        antialiasing: false,
        maxParticleCount: 50,
        lodDistance: 20,
        autoRotateSpeed: 0.1,
        renderScale: 0.5,
        maxFPS: 30,
        weatherEnabled: false,
        postProcessingEnabled: false
      },
      medium: {
        complexityLevel: 2 as const,
        particlesEnabled: true,
        shadowsEnabled: false,
        antialiasing: false,
        maxParticleCount: 200,
        lodDistance: 40,
        autoRotateSpeed: 0.3,
        renderScale: 0.75,
        maxFPS: 45,
        weatherEnabled: true,
        postProcessingEnabled: false
      },
      high: {
        complexityLevel: 4 as const,
        particlesEnabled: true,
        shadowsEnabled: true,
        antialiasing: true,
        maxParticleCount: 1000,
        lodDistance: 80,
        autoRotateSpeed: 0.5,
        renderScale: 1.0,
        maxFPS: 60,
        weatherEnabled: true,
        postProcessingEnabled: true
      }
    }
    
    let settings = { ...baseSettings[performanceLevel] }
    
    // Mobile-specific adjustments
    if (isMobile) {
      settings.complexityLevel = Math.min(settings.complexityLevel, 2) as 1 | 2 | 3 | 4
      settings.shadowsEnabled = false
      settings.maxParticleCount = Math.floor(settings.maxParticleCount * 0.5)
      settings.renderScale = Math.min(settings.renderScale, 0.8)
      settings.postProcessingEnabled = false
    }
    
    // Screen size adjustments
    if (screenSize === 'small') {
      settings.renderScale *= 0.8
      settings.maxParticleCount = Math.floor(settings.maxParticleCount * 0.6)
      settings.lodDistance *= 0.7
    }
    
    // Memory adjustments
    if (memoryLevel === 'low') {
      settings.complexityLevel = Math.min(settings.complexityLevel, 1) as 1 | 2 | 3 | 4
      settings.maxParticleCount = Math.floor(settings.maxParticleCount * 0.4)
      settings.weatherEnabled = false
    }
    
    // Connection-based adjustments
    if (connectionType === 'slow-2g' || connectionType === '2g') {
      settings.complexityLevel = 1
      settings.particlesEnabled = false
      settings.weatherEnabled = false
    }
    
    return settings
  }

  private setupPerformanceMonitoring() {
    // Monitor FPS and adjust settings dynamically
    let frameCount = 0
    let lastTime = performance.now()
    let fpsHistory: number[] = []
    
    const measurePerformance = () => {
      frameCount++
      const currentTime = performance.now()
      
      if (currentTime - lastTime >= 1000) {
        const fps = Math.round((frameCount * 1000) / (currentTime - lastTime))
        fpsHistory.push(fps)
        
        // Keep only last 10 seconds of FPS data
        if (fpsHistory.length > 10) {
          fpsHistory = fpsHistory.slice(-10)
        }
        
        // Check if performance is consistently poor
        const averageFPS = fpsHistory.reduce((a, b) => a + b, 0) / fpsHistory.length
        
        if (fpsHistory.length >= 5 && averageFPS < 25) {
          this.adaptToLowPerformance()
        } else if (fpsHistory.length >= 5 && averageFPS > 50) {
          this.adaptToHighPerformance()
        }
        
        frameCount = 0
        lastTime = currentTime
      }
      
      requestAnimationFrame(measurePerformance)
    }
    
    requestAnimationFrame(measurePerformance)
  }

  private setupResizeObserver() {
    this.resizeObserver = new ResizeObserver((entries) => {
      const entry = entries[0]
      if (entry) {
        const { width, height } = entry.contentRect
        
        // Update device info
        this.deviceInfo.orientation = height > width ? 'portrait' : 'landscape'
        
        if (width < 576) this.deviceInfo.screenSize = 'small'
        else if (width < 768) this.deviceInfo.screenSize = 'medium'
        else if (width < 1200) this.deviceInfo.screenSize = 'large'  
        else this.deviceInfo.screenSize = 'xl'
        
        // Notify listeners of new optimal settings
        this.notifyListeners()
      }
    })
    
    this.resizeObserver.observe(document.body)
  }

  private adaptToLowPerformance() {
    const settings = this.getOptimalSettings()
    
    // Further reduce settings for poor performance
    settings.complexityLevel = Math.max(1, settings.complexityLevel - 1) as 1 | 2 | 3 | 4
    settings.maxParticleCount = Math.floor(settings.maxParticleCount * 0.5)
    settings.renderScale = Math.max(0.5, settings.renderScale - 0.1)
    settings.shadowsEnabled = false
    settings.postProcessingEnabled = false
    
    this.notifyListeners(settings)
  }

  private adaptToHighPerformance() {
    const settings = this.getOptimalSettings()
    
    // Slightly increase settings for good performance
    if (settings.complexityLevel < 3 && this.deviceInfo.performanceLevel !== 'low') {
      settings.complexityLevel = Math.min(4, settings.complexityLevel + 1) as 1 | 2 | 3 | 4
      settings.renderScale = Math.min(1.0, settings.renderScale + 0.1)
    }
    
    this.notifyListeners(settings)
  }

  private notifyListeners(settings?: OptimizationSettings) {
    const optimalSettings = settings || this.getOptimalSettings()
    this.listeners.forEach(listener => listener(optimalSettings))
  }

  // Public API
  getDeviceInfo(): DeviceInfo {
    return { ...this.deviceInfo }
  }

  getOptimizationSettings(): OptimizationSettings {
    return this.getOptimalSettings()
  }

  onSettingsChange(callback: (settings: OptimizationSettings) => void) {
    this.listeners.push(callback)
    
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(callback)
      if (index > -1) {
        this.listeners.splice(index, 1)
      }
    }
  }

  // Touch-specific optimizations
  getTouchOptimizations() {
    if (!this.deviceInfo.hasTouch) return {}
    
    return {
      // Larger touch targets
      minimumTouchTarget: 44, // 44px minimum
      
      // Touch-friendly interactions
      tapDelay: 0,
      doubleTapZoom: false,
      
      // Gesture handling
      preventDefaultTouchMove: true,
      
      // Performance
      passiveEventListeners: true
    }
  }

  // CSS media queries for responsive design
  getResponsiveBreakpoints() {
    return {
      small: '(max-width: 575px)',
      medium: '(min-width: 576px) and (max-width: 767px)',
      large: '(min-width: 768px) and (max-width: 1199px)',
      xl: '(min-width: 1200px)',
      portrait: '(orientation: portrait)',
      landscape: '(orientation: landscape)',
      retina: `(-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi)`,
      lowMemory: `(max-device-width: 768px) and (max-device-height: 1024px)`,
      touch: '(pointer: coarse)',
      mouse: '(pointer: fine)'
    }
  }

  // Cleanup
  dispose() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect()
    }
    this.listeners = []
  }
}

// Singleton instance
export const mobileOptimizationService = new MobileOptimizationService()

// Utility functions
export function isMobileDevice(): boolean {
  return mobileOptimizationService.getDeviceInfo().isMobile
}

export function getOptimalComplexityLevel(): 1 | 2 | 3 | 4 {
  return mobileOptimizationService.getOptimizationSettings().complexityLevel
}

export function shouldEnableFeature(feature: keyof OptimizationSettings): boolean {
  const settings = mobileOptimizationService.getOptimizationSettings()
  return Boolean(settings[feature])
}

// React hook for responsive design
export function useResponsiveDesign() {
  const [deviceInfo, setDeviceInfo] = React.useState(mobileOptimizationService.getDeviceInfo())
  const [settings, setSettings] = React.useState(mobileOptimizationService.getOptimizationSettings())
  
  React.useEffect(() => {
    const unsubscribe = mobileOptimizationService.onSettingsChange((newSettings) => {
      setSettings(newSettings)
      setDeviceInfo(mobileOptimizationService.getDeviceInfo())
    })
    
    return unsubscribe
  }, [])
  
  return { deviceInfo, settings }
}

export type { DeviceInfo, OptimizationSettings }