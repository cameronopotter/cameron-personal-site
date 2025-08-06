import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, act, waitFor } from '@testing-library/react'
import { PerformanceMonitor } from '@/components/PerformanceMonitor'
import { measurePerformance } from '@tests/utils/testUtils'

// Mock performance API
const mockPerformance = {
  now: vi.fn(),
  mark: vi.fn(),
  measure: vi.fn(),
  getEntriesByName: vi.fn(),
  getEntriesByType: vi.fn(),
  clearMarks: vi.fn(),
  clearMeasures: vi.fn()
}

Object.defineProperty(global, 'performance', {
  writable: true,
  value: mockPerformance
})

describe('PerformanceMonitor', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    mockPerformance.now.mockReturnValue(0)
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  it('renders performance metrics correctly', async () => {
    render(<PerformanceMonitor />)
    
    expect(screen.getByTestId('performance-monitor')).toBeInTheDocument()
    expect(screen.getByText(/fps/i)).toBeInTheDocument()
    expect(screen.getByText(/memory/i)).toBeInTheDocument()
    expect(screen.getByText(/render time/i)).toBeInTheDocument()
  })

  it('tracks FPS accurately', async () => {
    render(<PerformanceMonitor />)
    
    // Simulate frame updates
    let frameCount = 0
    const simulateFrames = async (count: number) => {
      for (let i = 0; i < count; i++) {
        frameCount++
        mockPerformance.now.mockReturnValue(frameCount * 16.67) // 60 FPS
        
        await act(async () => {
          // Trigger frame update
          window.dispatchEvent(new Event('beforeunload'))
        })
      }
    }

    await simulateFrames(60) // 1 second of 60 FPS
    
    await waitFor(() => {
      const fpsDisplay = screen.getByTestId('fps-counter')
      expect(fpsDisplay).toBeInTheDocument()
      // Should show approximately 60 FPS
      expect(fpsDisplay.textContent).toContain('60')
    })
  })

  it('detects performance bottlenecks', async () => {
    render(<PerformanceMonitor showWarnings={true} />)
    
    // Simulate slow frame
    mockPerformance.now
      .mockReturnValueOnce(0)
      .mockReturnValueOnce(100) // 100ms frame time = 10 FPS
    
    await act(async () => {
      window.dispatchEvent(new Event('beforeunload'))
    })
    
    await waitFor(() => {
      expect(screen.getByTestId('performance-warning')).toBeInTheDocument()
      expect(screen.getByText(/low fps detected/i)).toBeInTheDocument()
    })
  })

  it('monitors memory usage', async () => {
    // Mock memory API
    Object.defineProperty(performance, 'memory', {
      writable: true,
      value: {
        usedJSHeapSize: 50 * 1024 * 1024, // 50MB
        totalJSHeapSize: 100 * 1024 * 1024, // 100MB
        jsHeapSizeLimit: 2 * 1024 * 1024 * 1024 // 2GB
      }
    })

    render(<PerformanceMonitor showMemory={true} />)
    
    await waitFor(() => {
      const memoryDisplay = screen.getByTestId('memory-usage')
      expect(memoryDisplay).toBeInTheDocument()
      expect(memoryDisplay.textContent).toContain('50')
    })
  })

  it('tracks render time distribution', async () => {
    render(<PerformanceMonitor />)
    
    const renderTimes = [10, 15, 12, 18, 14, 16, 13, 17, 11, 19]
    
    for (const [index, time] of renderTimes.entries()) {
      mockPerformance.now
        .mockReturnValueOnce(index * 16.67)
        .mockReturnValueOnce(index * 16.67 + time)
      
      await act(async () => {
        window.dispatchEvent(new Event('beforeunload'))
      })
    }
    
    await waitFor(() => {
      const renderTimeDisplay = screen.getByTestId('render-time')
      expect(renderTimeDisplay).toBeInTheDocument()
      
      // Should show average render time
      const avgTime = renderTimes.reduce((sum, time) => sum + time, 0) / renderTimes.length
      expect(renderTimeDisplay.textContent).toContain(avgTime.toFixed(1))
    })
  })

  it('provides performance optimization suggestions', async () => {
    render(<PerformanceMonitor showSuggestions={true} />)
    
    // Simulate performance issues
    mockPerformance.now
      .mockReturnValueOnce(0)
      .mockReturnValueOnce(50) // Very slow frame
    
    await act(async () => {
      window.dispatchEvent(new Event('beforeunload'))
    })
    
    await waitFor(() => {
      expect(screen.getByTestId('performance-suggestions')).toBeInTheDocument()
      expect(screen.getByText(/reduce draw calls/i)).toBeInTheDocument()
    })
  })

  it('exports performance data correctly', async () => {
    const onExport = vi.fn()
    render(<PerformanceMonitor onExport={onExport} />)
    
    // Generate some performance data
    const frames = 100
    for (let i = 0; i < frames; i++) {
      mockPerformance.now
        .mockReturnValueOnce(i * 16.67)
        .mockReturnValueOnce(i * 16.67 + 15) // Consistent 15ms render time
      
      await act(async () => {
        window.dispatchEvent(new Event('beforeunload'))
      })
    }
    
    const exportButton = screen.getByTestId('export-performance-data')
    await act(async () => {
      exportButton.click()
    })
    
    expect(onExport).toHaveBeenCalledWith(
      expect.objectContaining({
        fps: expect.any(Number),
        renderTime: expect.any(Number),
        memoryUsage: expect.any(Number),
        timestamp: expect.any(Number)
      })
    )
  })

  it('handles high-frequency updates efficiently', async () => {
    const { rerender } = render(<PerformanceMonitor />)
    
    const updateOperation = async () => {
      mockPerformance.now.mockReturnValue(Date.now())
      rerender(<PerformanceMonitor />)
    }

    const performance = await measurePerformance(updateOperation, 100)
    
    // Updates should be efficient
    expect(performance.avg).toBeLessThan(5) // Under 5ms average
    expect(performance.max).toBeLessThan(20) // Under 20ms maximum
  })

  it('throttles updates to prevent spam', async () => {
    const onUpdate = vi.fn()
    render(<PerformanceMonitor onUpdate={onUpdate} updateInterval={100} />)
    
    // Trigger many rapid updates
    for (let i = 0; i < 10; i++) {
      await act(async () => {
        window.dispatchEvent(new Event('beforeunload'))
      })
    }
    
    // Should only call onUpdate once due to throttling
    expect(onUpdate).toHaveBeenCalledTimes(1)
    
    // Advance time and trigger another update
    await act(async () => {
      vi.advanceTimersByTime(150)
      window.dispatchEvent(new Event('beforeunload'))
    })
    
    expect(onUpdate).toHaveBeenCalledTimes(2)
  })

  it('maintains performance history', async () => {
    render(<PerformanceMonitor historySize={50} />)
    
    // Generate performance history
    for (let i = 0; i < 60; i++) {
      mockPerformance.now
        .mockReturnValueOnce(i * 16.67)
        .mockReturnValueOnce(i * 16.67 + 16)
      
      await act(async () => {
        window.dispatchEvent(new Event('beforeunload'))
      })
    }
    
    const historyDisplay = screen.getByTestId('performance-history')
    expect(historyDisplay).toBeInTheDocument()
    
    // Should only keep the last 50 entries
    const historyItems = screen.getAllByTestId('history-item')
    expect(historyItems).toHaveLength(50)
  })
})