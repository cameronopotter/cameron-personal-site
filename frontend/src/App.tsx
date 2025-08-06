import React, { Suspense, useEffect, useState, useDeferredValue } from 'react'
import { Box, CircularProgress, Alert, Fade } from '@mui/material'
import { AnimatePresence } from 'framer-motion'
import { useHotkeys } from 'react-hotkeys-hook'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { useGardenStore } from '@/stores/gardenStore'
import { useWebSocket } from '@/hooks/useWebSocket'
import { usePerformanceMonitor } from '@/hooks/usePerformanceMonitor'
import { LoadingScreen } from '@/components/LoadingScreen'
import { GardenCanvas } from '@/components/GardenCanvas'
import { NavigationOverlay } from '@/components/NavigationOverlay'
import { ProjectModal } from '@/components/ProjectModal'
import { SkillConstellationModal } from '@/components/SkillConstellationModal'
import { SettingsPanel } from '@/components/SettingsPanel'
import { NotificationSystem } from '@/components/NotificationSystem'
import { PerformanceMonitor } from '@/components/PerformanceMonitor'
import { AccessibilityProvider } from '@/providers/AccessibilityProvider'
import type { ComplexityLevel } from '@/types'

const App: React.FC = () => {
  const [isInitialized, setIsInitialized] = useState(false)
  const [initError, setInitError] = useState<string | null>(null)
  
  // Garden state management
  const {
    selectedProject,
    selectedSkill,
    ui,
    settings,
    performance,
    setComplexityLevel,
    updateSettings,
    showNotification,
    trackInteraction
  } = useGardenStore()
  
  // Deferred value for performance optimization
  const deferredSelectedProject = useDeferredValue(selectedProject)
  
  // Real-time WebSocket connection
  const { isConnected, error: wsError } = useWebSocket()
  
  // Performance monitoring
  const { fps, renderTime, isOptimizing } = usePerformanceMonitor()
  
  // Adaptive complexity based on performance
  useEffect(() => {
    let newComplexity: ComplexityLevel = settings.complexityLevel
    
    if (isOptimizing || fps < 30) {
      newComplexity = Math.max(1, settings.complexityLevel - 1) as ComplexityLevel
    } else if (fps > 55 && renderTime < 16) {
      newComplexity = Math.min(4, settings.complexityLevel + 1) as ComplexityLevel
    }
    
    if (newComplexity !== settings.complexityLevel) {
      setComplexityLevel(newComplexity)
    }
  }, [fps, renderTime, isOptimizing, settings.complexityLevel, setComplexityLevel])
  
  // Initialize application
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Check device capabilities
        const capabilities = await checkDeviceCapabilities()
        
        // Set initial complexity level based on device
        const initialComplexity: ComplexityLevel = capabilities.webgl2 
          ? (capabilities.highPerformance ? 4 : 3)
          : (capabilities.webgl ? 2 : 1)
        
        setComplexityLevel(initialComplexity)
        
        // Load initial garden data
        await loadInitialData()
        
        // Initialize accessibility features
        initializeAccessibility()
        
        setIsInitialized(true)
        
        // Track initialization
        trackInteraction({
          type: 'focus',
          target: 'app',
          metadata: {
            initialComplexity,
            webSocketConnected: isConnected,
            capabilities
          }
        })
        
      } catch (error) {
        console.error('Failed to initialize app:', error)
        setInitError(error instanceof Error ? error.message : 'Unknown initialization error')
      }
    }
    
    initializeApp()
  }, [setComplexityLevel, trackInteraction, isConnected])
  
  // Keyboard shortcuts
  useHotkeys('space', () => {
    trackInteraction({ type: 'click', target: 'keyboard-shortcut-space' })
  })
  
  useHotkeys('escape', () => {
    if (selectedProject) {
      useGardenStore.getState().selectProject(null)
    } else if (selectedSkill) {
      useGardenStore.getState().selectSkill(null)
    } else if (ui.activeModal) {
      useGardenStore.getState().closeModal()
    }
  })
  
  useHotkeys('1,2,3,4', (event) => {
    const level = parseInt(event.key) as ComplexityLevel
    setComplexityLevel(level)
    showNotification({
      type: 'info',
      message: `Complexity level set to ${level}`,
      duration: 2000,
      persistent: false
    })
  })
  
  // Show WebSocket connection status
  useEffect(() => {
    if (wsError) {
      showNotification({
        type: 'warning',
        message: 'Real-time features may be limited',
        duration: 5000,
        persistent: false
      })
    }
  }, [wsError, showNotification])
  
  // Error state
  if (initError) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          gap: 2,
          p: 4
        }}
      >
        <Alert severity="error" sx={{ maxWidth: 600 }}>
          Failed to initialize Digital Greenhouse: {initError}
        </Alert>
      </Box>
    )
  }
  
  // Loading state
  if (!isInitialized) {
    return <LoadingScreen />
  }
  
  return (
    <AccessibilityProvider>
      <ErrorBoundary>
        <Box
          sx={{
            width: '100vw',
            height: '100vh',
            overflow: 'hidden',
            position: 'relative',
            background: 'linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%)'
          }}
          role="application"
          aria-label="Cameron Potter's Digital Greenhouse Portfolio"
        >
          {/* Main 3D Garden Canvas */}
          <Suspense fallback={<LoadingScreen message="Loading 3D Garden..." />}>
            <GardenCanvas />
          </Suspense>
          
          {/* Navigation Overlay */}
          <NavigationOverlay />
          
          {/* Modals and Overlays */}
          <AnimatePresence mode="wait">
            {deferredSelectedProject && (
              <ProjectModal
                key={`project-${deferredSelectedProject.id}`}
                project={deferredSelectedProject}
                open={Boolean(deferredSelectedProject)}
                onClose={() => useGardenStore.getState().selectProject(null)}
              />
            )}
            
            {selectedSkill && (
              <SkillConstellationModal
                key={`skill-${selectedSkill.id}`}
                skill={selectedSkill}
                open={Boolean(selectedSkill)}
                onClose={() => useGardenStore.getState().selectSkill(null)}
              />
            )}
            
            {ui.settingsOpen && (
              <SettingsPanel
                open={ui.settingsOpen}
                onClose={() => updateSettings({ settingsOpen: false })}
              />
            )}
          </AnimatePresence>
          
          {/* Notification System */}
          <NotificationSystem />
          
          {/* Performance Monitor (dev mode only) */}
          {import.meta.env.DEV && <PerformanceMonitor />}
          
          {/* Loading States */}
          {Object.values(ui.loadingStates).some(Boolean) && (
            <Fade in>
              <Box
                sx={{
                  position: 'fixed',
                  bottom: 24,
                  right: 24,
                  zIndex: 1000
                }}
              >
                <CircularProgress size={24} color="primary" />
              </Box>
            </Fade>
          )}
          
          {/* Accessibility Announcements */}
          <Box
            id="garden-announcements"
            aria-live="polite"
            aria-atomic="true"
            sx={{
              position: 'absolute',
              left: -10000,
              width: 1,
              height: 1,
              overflow: 'hidden'
            }}
          >
            {selectedProject && `Now viewing project: ${selectedProject.name}`}
            {selectedSkill && `Now viewing skill: ${selectedSkill.name}`}
          </Box>
        </Box>
      </ErrorBoundary>
    </AccessibilityProvider>
  )
}

// Device capability detection
async function checkDeviceCapabilities() {
  const canvas = document.createElement('canvas')
  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl')
  const gl2 = canvas.getContext('webgl2')
  
  const capabilities = {
    webgl: Boolean(gl),
    webgl2: Boolean(gl2),
    maxTextureSize: gl?.getParameter(gl.MAX_TEXTURE_SIZE) || 0,
    maxRenderBufferSize: gl?.getParameter(gl.MAX_RENDERBUFFER_SIZE) || 0,
    highPerformance: false,
    deviceMemory: (navigator as any).deviceMemory || 4,
    hardwareConcurrency: navigator.hardwareConcurrency || 4
  }
  
  // Simple performance test
  if (gl) {
    const start = performance.now()
    for (let i = 0; i < 1000; i++) {
      gl.createBuffer()
    }
    const duration = performance.now() - start
    capabilities.highPerformance = duration < 50
  }
  
  return capabilities
}

// Load initial data
async function loadInitialData() {
  // This would normally fetch from the backend API
  // For now, we'll initialize with default data
  const { initializeWithDefaults } = useGardenStore.getState()
  initializeWithDefaults?.()
}

// Initialize accessibility features
function initializeAccessibility() {
  // Check for reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  
  if (prefersReducedMotion) {
    useGardenStore.getState().updateSettings({
      complexityLevel: 1,
      particlesEnabled: false,
      autoRotate: false
    })
  }
  
  // Check for high contrast preference
  const prefersHighContrast = window.matchMedia('(prefers-contrast: high)').matches
  
  if (prefersHighContrast) {
    useGardenStore.getState().updateSettings({
      theme: 'dark' // High contrast theme would be implemented
    })
  }
}

export default App