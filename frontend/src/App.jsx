import React, { Suspense, useEffect } from 'react'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import { Box } from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'
import { useGardenStore } from './stores/gardenStore'
import { GardenCanvas } from './components/GardenCanvas'
import { NavigationOverlay } from './components/NavigationOverlay'
import { ProjectModal } from './components/ProjectModal'
import { LoadingScreen } from './components/LoadingScreen'
import { ErrorBoundary } from './components/ErrorBoundary'
import { NotificationSystem } from './components/NotificationSystem'
import { SettingsPanel } from './components/SettingsPanel'
import { AccessibilityProvider } from './providers/AccessibilityProvider'
import { useWebSocket } from './hooks/useWebSocket'
import { usePerformanceMonitor } from './hooks/usePerformanceMonitor'
import { apiService } from './services/api'
import './index.css'

// Create dark theme optimized for 3D content
const createGardenTheme = (season) => {
  const seasonalColors = {
    spring: {
      primary: '#4CAF50',
      secondary: '#8BC34A', 
      accent: '#2196F3',
      background: '#0a1a0a'
    },
    summer: {
      primary: '#2E7D32',
      secondary: '#FF9800',
      accent: '#9C27B0', 
      background: '#0f1a0a'
    },
    autumn: {
      primary: '#FFC107',
      secondary: '#F44336',
      accent: '#FF5722',
      background: '#1a150a'
    },
    winter: {
      primary: '#1976D2',
      secondary: '#9E9E9E',
      accent: '#FAFAFA',
      background: '#0a0f1a'
    }
  }

  const colors = seasonalColors[season] || seasonalColors.spring

  return createTheme({
    palette: {
      mode: 'dark',
      primary: { main: colors.primary },
      secondary: { main: colors.secondary },
      background: {
        default: colors.background,
        paper: 'rgba(26, 26, 26, 0.8)'
      },
      text: {
        primary: '#ffffff',
        secondary: 'rgba(255, 255, 255, 0.7)'
      }
    },
    typography: {
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      h1: { fontWeight: 300, letterSpacing: '-0.02em' },
      h2: { fontWeight: 300, letterSpacing: '-0.01em' },
      h3: { fontWeight: 400 },
      body1: { lineHeight: 1.6 },
      body2: { lineHeight: 1.5 }
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 12,
            textTransform: 'none',
            fontWeight: 500,
            backdropFilter: 'blur(10px)',
            background: 'rgba(255, 255, 255, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            '&:hover': {
              background: 'rgba(255, 255, 255, 0.2)',
              transform: 'translateY(-1px)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
            }
          }
        }
      },
      MuiCard: {
        styleOverrides: {
          root: {
            background: 'rgba(26, 26, 26, 0.9)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 16,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
          }
        }
      },
      MuiDialog: {
        styleOverrides: {
          paper: {
            background: 'rgba(26, 26, 26, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 16
          }
        }
      }
    }
  })
}

function App() {
  const { 
    season,
    selectedProject,
    ui,
    initializeWithDefaults,
    showNotification,
    updateRealtimeData,
    selectProject,
    selectSkill
  } = useGardenStore()

  // Create theme based on current season
  const theme = createGardenTheme(season)

  // Initialize WebSocket connection for real-time updates
  const { connected, lastMessage } = useWebSocket('ws://localhost:8000/ws/garden')

  // Performance monitoring
  usePerformanceMonitor()

  // Initialize garden state and load data from API
  useEffect(() => {
    const initializeGarden = async () => {
      try {
        // Initialize with defaults first
        initializeWithDefaults()

        // Load initial data from API
        const gardenData = await apiService.getGardenState()
        if (gardenData) {
          updateRealtimeData({
            activeVisitors: gardenData.activeVisitors || 1,
            weatherUpdates: gardenData.weather,
            projectGrowthUpdates: gardenData.projects || [],
            systemHealth: gardenData.systemHealth || {
              performance: 0.95,
              loadTime: 1200,
              errorRate: 0.01
            }
          })

          showNotification({
            type: 'success',
            title: 'Garden Initialized',
            message: 'Welcome to your Digital Greenhouse! 🌱',
            duration: 3000
          })
        }
      } catch (error) {
        console.warn('Garden initialization with limited features:', error)
        showNotification({
          type: 'info',
          title: 'Garden Ready',
          message: 'Running in demo mode - connect to backend for full features',
          duration: 5000
        })
      }
    }

    initializeGarden()
  }, [initializeWithDefaults, updateRealtimeData, showNotification])

  // Handle WebSocket messages for real-time updates
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage)
        
        switch (data.type) {
          case 'weather_update':
            updateRealtimeData({ weatherUpdates: data.weather })
            break
          case 'project_growth':
            updateRealtimeData({ projectGrowthUpdates: [data.project] })
            break
          case 'visitor_joined':
            updateRealtimeData({ activeVisitors: data.count })
            break
          default:
            console.log('Unknown WebSocket message:', data)
        }
      } catch (error) {
        console.warn('Failed to parse WebSocket message:', error)
      }
    }
  }, [lastMessage, updateRealtimeData])

  // Show loading screen while garden initializes
  if (!season || !theme) {
    return <LoadingScreen message="Preparing your digital garden..." />
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AccessibilityProvider>
        <ErrorBoundary>
          <Box
            sx={{
              width: '100vw',
              height: '100vh',
              overflow: 'hidden',
              position: 'relative',
              background: `linear-gradient(135deg, ${theme.palette.background.default} 0%, rgba(0,0,0,0.8) 100%)`
            }}
          >
            {/* Main 3D Garden Canvas */}
            <Suspense fallback={<LoadingScreen message="Loading 3D garden..." />}>
              <GardenCanvas
                onProjectSelect={selectProject}
                onSkillSelect={selectSkill}
                className="garden-canvas"
              />
            </Suspense>

            {/* Navigation Overlay */}
            <NavigationOverlay
              connected={connected}
              onNavigate={(mode) => {
                useGardenStore.getState().setNavigationMode(mode)
              }}
            />

            {/* Project Detail Modal */}
            <AnimatePresence>
              {selectedProject && (
                <ProjectModal
                  project={selectedProject}
                  open={Boolean(selectedProject)}
                  onClose={() => selectProject(null)}
                />
              )}
            </AnimatePresence>

            {/* Settings Panel */}
            <AnimatePresence>
              {ui.settingsOpen && (
                <SettingsPanel
                  open={ui.settingsOpen}
                  onClose={() => useGardenStore.getState().openModal(null)}
                />
              )}
            </AnimatePresence>

            {/* Notification System */}
            <NotificationSystem />

            {/* Performance and Accessibility Indicators */}
            <motion.div
              style={{
                position: 'fixed',
                bottom: 16,
                right: 16,
                zIndex: 1000,
                display: 'flex',
                flexDirection: 'column',
                gap: 8,
                pointerEvents: 'none'
              }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 2, duration: 0.5 }}
            >
              {/* Connection Status Indicator */}
              <Box
                sx={{
                  px: 2,
                  py: 1,
                  background: connected 
                    ? 'rgba(76, 175, 80, 0.2)' 
                    : 'rgba(255, 152, 0, 0.2)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: 2,
                  border: `1px solid ${connected ? '#4CAF50' : '#FF9800'}`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  fontSize: '0.75rem',
                  color: connected ? '#4CAF50' : '#FF9800'
                }}
              >
                <Box
                  component="span"
                  sx={{
                    width: 6,
                    height: 6,
                    borderRadius: '50%',
                    backgroundColor: 'currentColor',
                    animation: connected ? 'pulse 2s infinite' : 'none'
                  }}
                />
                {connected ? 'Connected' : 'Offline Mode'}
              </Box>
            </motion.div>
          </Box>
        </ErrorBoundary>
      </AccessibilityProvider>

      {/* Global Styles */}
      <style jsx global>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        
        .garden-canvas {
          transition: filter 0.3s ease;
        }
        
        .garden-canvas.modal-open {
          filter: blur(2px) brightness(0.7);
        }
        
        /* Accessibility improvements */
        @media (prefers-reduced-motion: reduce) {
          * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
          }
        }
        
        /* High contrast mode */
        @media (prefers-contrast: high) {
          .garden-canvas {
            filter: contrast(1.5) brightness(1.2);
          }
        }
        
        /* Focus visibility */
        button:focus-visible,
        [role="button"]:focus-visible {
          outline: 2px solid ${theme.palette.primary.main};
          outline-offset: 2px;
        }
      `}</style>
    </ThemeProvider>
  )
}

export default App