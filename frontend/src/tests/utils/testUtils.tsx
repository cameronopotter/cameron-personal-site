import React, { ReactElement } from 'react'
import { render, RenderOptions, RenderResult } from '@testing-library/react'
import { Canvas } from '@react-three/fiber'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import { AccessibilityProvider } from '@/providers/AccessibilityProvider'
import { vi } from 'vitest'

// Create theme for testing
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#4CAF50' },
    secondary: { main: '#FF6B35' }
  }
})

// Test providers wrapper
interface AllTheProvidersProps {
  children: React.ReactNode
}

const AllTheProviders: React.FC<AllTheProvidersProps> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  })

  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <AccessibilityProvider>
            {children}
          </AccessibilityProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </BrowserRouter>
  )
}

// Custom render function with providers
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
): RenderResult => render(ui, { wrapper: AllTheProviders, ...options })

// Three.js specific render helper
export const renderWithThree = (
  ui: ReactElement,
  options?: {
    camera?: any
    scene?: any
    frameloop?: 'always' | 'demand' | 'never'
  }
): RenderResult => {
  const ThreeWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <AllTheProviders>
      <Canvas
        camera={options?.camera}
        scene={options?.scene}
        frameloop={options?.frameloop || 'never'}
        gl={{ antialias: false, alpha: false }}
        style={{ width: '100px', height: '100px' }}
      >
        {children}
      </Canvas>
    </AllTheProviders>
  )
  
  return render(ui, { wrapper: ThreeWrapper })
}

// Mock WebSocket connection for testing
export const createMockWebSocket = () => {
  const mockWs = {
    readyState: WebSocket.OPEN,
    send: vi.fn(),
    close: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    onopen: null,
    onclose: null,
    onmessage: null,
    onerror: null
  }
  
  // Helper to simulate receiving messages
  const simulateMessage = (data: any) => {
    if (mockWs.onmessage) {
      mockWs.onmessage({ data: JSON.stringify(data) } as MessageEvent)
    }
  }
  
  // Helper to simulate connection events
  const simulateOpen = () => {
    if (mockWs.onopen) {
      mockWs.onopen({} as Event)
    }
  }
  
  const simulateClose = () => {
    if (mockWs.onclose) {
      mockWs.onclose({} as CloseEvent)
    }
  }
  
  return { mockWs, simulateMessage, simulateOpen, simulateClose }
}

// Performance testing utilities
export const measurePerformance = async (
  operation: () => Promise<void> | void,
  iterations = 100
) => {
  const times: number[] = []
  
  for (let i = 0; i < iterations; i++) {
    const start = performance.now()
    await operation()
    const end = performance.now()
    times.push(end - start)
  }
  
  const avg = times.reduce((sum, time) => sum + time, 0) / times.length
  const min = Math.min(...times)
  const max = Math.max(...times)
  const median = times.sort()[Math.floor(times.length / 2)]
  
  return { avg, min, max, median, times }
}

// Accessibility testing helpers
export const axeMatchers = {
  toHaveNoViolations: (received: any) => {
    const violations = received.violations || []
    const pass = violations.length === 0
    
    return {
      pass,
      message: () =>
        pass
          ? 'Expected element to have accessibility violations'
          : `Expected element to have no accessibility violations but found:\n${violations
              .map((v: any) => `  - ${v.id}: ${v.description}`)
              .join('\n')}`
    }
  }
}

// Mock intersection observer entries
export const createMockIntersectionEntry = (
  isIntersecting: boolean,
  intersectionRatio = isIntersecting ? 1 : 0
) => ({
  isIntersecting,
  intersectionRatio,
  intersectionRect: { top: 0, left: 0, bottom: 0, right: 0, width: 0, height: 0 },
  boundingClientRect: { top: 0, left: 0, bottom: 100, right: 100, width: 100, height: 100 },
  rootBounds: { top: 0, left: 0, bottom: 800, right: 600, width: 600, height: 800 },
  target: document.createElement('div'),
  time: Date.now()
})

// Mock user preferences for testing
export const mockUserPreferences = {
  reducedMotion: false,
  highContrast: false,
  largeText: false,
  soundEnabled: true
}

// Re-export everything from testing library
export * from '@testing-library/react'
export { customRender as render }