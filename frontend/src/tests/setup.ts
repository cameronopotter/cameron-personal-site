import '@testing-library/jest-dom'
import { vi } from 'vitest'
import { configure } from '@testing-library/react'
import { TextEncoder, TextDecoder } from 'util'

// Configure testing library
configure({
  testIdAttribute: 'data-testid'
})

// Global polyfills for jsdom
Object.assign(global, {
  TextEncoder,
  TextDecoder
})

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
  root: null,
  rootMargin: '',
  thresholds: []
}))

// Mock WebGL context
HTMLCanvasElement.prototype.getContext = vi.fn((contextType: string) => {
  if (contextType === 'webgl' || contextType === 'webgl2') {
    return {
      canvas: document.createElement('canvas'),
      drawingBufferWidth: 1920,
      drawingBufferHeight: 1080,
      getParameter: vi.fn(),
      getExtension: vi.fn(),
      createProgram: vi.fn(),
      createShader: vi.fn(),
      shaderSource: vi.fn(),
      compileShader: vi.fn(),
      attachShader: vi.fn(),
      linkProgram: vi.fn(),
      useProgram: vi.fn(),
      getAttribLocation: vi.fn(),
      getUniformLocation: vi.fn(),
      enableVertexAttribArray: vi.fn(),
      vertexAttribPointer: vi.fn(),
      uniform1f: vi.fn(),
      uniform2f: vi.fn(),
      uniform3f: vi.fn(),
      uniform4f: vi.fn(),
      uniformMatrix4fv: vi.fn(),
      createBuffer: vi.fn(),
      bindBuffer: vi.fn(),
      bufferData: vi.fn(),
      clear: vi.fn(),
      clearColor: vi.fn(),
      enable: vi.fn(),
      disable: vi.fn(),
      depthFunc: vi.fn(),
      viewport: vi.fn(),
      drawArrays: vi.fn(),
      drawElements: vi.fn(),
      finish: vi.fn()
    }
  }
  return null
})

// Mock requestAnimationFrame
global.requestAnimationFrame = vi.fn((cb: FrameRequestCallback) => {
  setTimeout(cb, 16) // ~60fps
  return 1
})

global.cancelAnimationFrame = vi.fn()

// Mock performance API
Object.defineProperty(window, 'performance', {
  writable: true,
  value: {
    now: vi.fn(() => Date.now()),
    mark: vi.fn(),
    measure: vi.fn(),
    getEntriesByName: vi.fn(() => []),
    getEntriesByType: vi.fn(() => []),
    clearMarks: vi.fn(),
    clearMeasures: vi.fn()
  }
})

// Mock WebSocket
global.WebSocket = vi.fn().mockImplementation(() => ({
  close: vi.fn(),
  send: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  readyState: WebSocket.CONNECTING,
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3
}))

// Mock navigator.clipboard
Object.defineProperty(navigator, 'clipboard', {
  writable: true,
  value: {
    readText: vi.fn(() => Promise.resolve('')),
    writeText: vi.fn(() => Promise.resolve())
  }
})

// Mock environment variables
vi.mock('../../config/environment', () => ({
  API_BASE_URL: 'http://localhost:8000',
  WS_BASE_URL: 'ws://localhost:8000',
  NODE_ENV: 'test'
}))

// Global test utilities
export const createMockThreeScene = () => ({
  add: vi.fn(),
  remove: vi.fn(),
  children: [],
  traverse: vi.fn(),
  updateMatrixWorld: vi.fn()
})

export const createMockCamera = () => ({
  position: { x: 0, y: 0, z: 5 },
  lookAt: vi.fn(),
  updateProjectionMatrix: vi.fn(),
  aspect: 1.77,
  fov: 75,
  near: 0.1,
  far: 1000
})

export const createMockRenderer = () => ({
  render: vi.fn(),
  setSize: vi.fn(),
  setClearColor: vi.fn(),
  setPixelRatio: vi.fn(),
  domElement: document.createElement('canvas'),
  dispose: vi.fn()
})