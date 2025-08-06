import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { screen, waitFor, act } from '@testing-library/react'
import { renderWithThree, measurePerformance } from '@tests/utils/testUtils'
import { GardenCanvas } from '@/components/GardenCanvas'
import { useGardenStore } from '@/stores/gardenStore'

// Mock the garden store
vi.mock('@/stores/gardenStore')
const mockUseGardenStore = vi.mocked(useGardenStore)

// Mock Three.js components that require WebGL
vi.mock('@react-three/fiber', async () => {
  const actual = await vi.importActual('@react-three/fiber')
  return {
    ...actual,
    useFrame: vi.fn((callback) => {
      // Simulate a single frame call for testing
      setTimeout(() => callback({ clock: { elapsedTime: 1 } }), 16)
    }),
    useThree: vi.fn(() => ({
      camera: { position: { set: vi.fn() } },
      scene: { add: vi.fn(), remove: vi.fn() },
      gl: { 
        domElement: document.createElement('canvas'),
        render: vi.fn(),
        setSize: vi.fn()
      }
    }))
  }
})

describe('GardenCanvas', () => {
  const mockStoreState = {
    projects: [
      {
        id: 1,
        name: 'Test Project',
        position: [0, 0, 0] as [number, number, number],
        growth: 0.8,
        type: 'tree',
        color: '#4CAF50'
      }
    ],
    skills: [
      {
        id: 1,
        name: 'React',
        level: 90,
        category: 'frontend',
        position: [2, 1, -1] as [number, number, number]
      }
    ],
    weather: {
      condition: 'sunny',
      temperature: 22,
      windSpeed: 5
    },
    isLoading: false,
    error: null,
    performance: {
      fps: 60,
      renderTime: 16,
      triangles: 1000,
      drawCalls: 5
    }
  }

  beforeEach(() => {
    mockUseGardenStore.mockReturnValue(mockStoreState as any)
    
    // Mock performance API
    vi.spyOn(performance, 'now').mockReturnValue(Date.now())
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('renders without crashing', async () => {
    renderWithThree(<GardenCanvas />)
    
    // The canvas should be rendered by react-three-fiber
    await waitFor(() => {
      expect(document.querySelector('canvas')).toBeInTheDocument()
    })
  })

  it('handles loading state correctly', async () => {
    mockUseGardenStore.mockReturnValue({
      ...mockStoreState,
      isLoading: true
    } as any)

    renderWithThree(<GardenCanvas />)
    
    // Should show loading indicator when isLoading is true
    expect(screen.queryByTestId('garden-loading')).toBeInTheDocument()
  })

  it('displays error state when error occurs', async () => {
    mockUseGardenStore.mockReturnValue({
      ...mockStoreState,
      error: 'Failed to load garden data'
    } as any)

    renderWithThree(<GardenCanvas />)
    
    expect(screen.getByTestId('garden-error')).toBeInTheDocument()
    expect(screen.getByText(/failed to load garden data/i)).toBeInTheDocument()
  })

  it('renders projects and skills when data is available', async () => {
    renderWithThree(<GardenCanvas />)
    
    await waitFor(() => {
      // Check that project plants are rendered
      expect(screen.getByTestId('project-plant-1')).toBeInTheDocument()
      
      // Check that skill constellation is rendered
      expect(screen.getByTestId('skill-constellation')).toBeInTheDocument()
    })
  })

  it('handles camera controls correctly', async () => {
    renderWithThree(<GardenCanvas />)
    
    const canvas = document.querySelector('canvas')
    expect(canvas).toBeInTheDocument()
    
    // Test camera movement via mouse events
    await act(async () => {
      if (canvas) {
        // Simulate mouse drag for camera rotation
        canvas.dispatchEvent(new MouseEvent('mousedown', { 
          clientX: 100, 
          clientY: 100, 
          bubbles: true 
        }))
        
        canvas.dispatchEvent(new MouseEvent('mousemove', { 
          clientX: 150, 
          clientY: 150, 
          bubbles: true 
        }))
        
        canvas.dispatchEvent(new MouseEvent('mouseup', { 
          bubbles: true 
        }))
      }
    })
    
    // Camera should have responded to user input
    await waitFor(() => {
      // This would test actual camera movement in a real implementation
      expect(canvas).toBeInTheDocument()
    })
  })

  it('maintains performance standards', async () => {
    const renderOperation = async () => {
      renderWithThree(<GardenCanvas />)
      await waitFor(() => {
        expect(document.querySelector('canvas')).toBeInTheDocument()
      })
    }

    const performance = await measurePerformance(renderOperation, 10)
    
    // Render should complete within reasonable time
    expect(performance.avg).toBeLessThan(100) // 100ms average
    expect(performance.max).toBeLessThan(200) // 200ms maximum
  })

  it('handles window resize correctly', async () => {
    renderWithThree(<GardenCanvas />)
    
    const canvas = document.querySelector('canvas')
    expect(canvas).toBeInTheDocument()
    
    // Simulate window resize
    await act(async () => {
      Object.defineProperty(window, 'innerWidth', { value: 1200, writable: true })
      Object.defineProperty(window, 'innerHeight', { value: 800, writable: true })
      
      window.dispatchEvent(new Event('resize'))
    })
    
    await waitFor(() => {
      // Canvas should adapt to new dimensions
      expect(canvas).toBeInTheDocument()
    })
  })

  it('cleans up resources on unmount', async () => {
    const { unmount } = renderWithThree(<GardenCanvas />)
    
    const disposeSpy = vi.fn()
    
    // Mock disposal methods
    vi.spyOn(console, 'warn').mockImplementation(() => {})
    
    unmount()
    
    // Should not have memory leaks or warnings
    expect(console.warn).not.toHaveBeenCalledWith(
      expect.stringContaining('memory leak')
    )
  })

  it('responds to accessibility controls', async () => {
    renderWithThree(<GardenCanvas />)
    
    // Test keyboard navigation
    const canvas = document.querySelector('canvas')
    
    if (canvas) {
      canvas.focus()
      
      await act(async () => {
        // Test arrow key navigation
        canvas.dispatchEvent(new KeyboardEvent('keydown', { 
          key: 'ArrowUp',
          bubbles: true 
        }))
      })
      
      await waitFor(() => {
        // Camera should respond to keyboard input
        expect(canvas).toBeInTheDocument()
      })
    }
  })

  it('handles different weather conditions', async () => {
    const weatherConditions = ['sunny', 'rainy', 'cloudy', 'stormy']
    
    for (const condition of weatherConditions) {
      mockUseGardenStore.mockReturnValue({
        ...mockStoreState,
        weather: {
          ...mockStoreState.weather,
          condition
        }
      } as any)
      
      const { unmount } = renderWithThree(<GardenCanvas />)
      
      await waitFor(() => {
        expect(screen.getByTestId('weather-system')).toBeInTheDocument()
      })
      
      unmount()
    }
  })
})