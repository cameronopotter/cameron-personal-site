import { Vector3, Color } from 'three'

// Core Garden Types
export type Season = 'spring' | 'summer' | 'autumn' | 'winter'
export type TimeOfDay = 'dawn' | 'day' | 'dusk' | 'night'
export type WeatherMood = 'stormy' | 'sunny' | 'cloudy' | 'aurora' | 'starry'
export type NavigationMode = 'explore' | 'focus' | 'create'
export type GrowthStage = 'seed' | 'sprout' | 'growing' | 'blooming' | 'mature'
export type InteractionType = 'hover' | 'click' | 'longPress' | 'focus'
export type ComplexityLevel = 1 | 2 | 3 | 4

// Weather System
export interface WeatherState {
  mood: WeatherMood
  intensity: number // 0-1
  timeOfDay: TimeOfDay
  seasonalInfluence: number // 0-1
  particles: {
    type: 'rain' | 'snow' | 'sparkles' | 'leaves' | 'aurora'
    density: number
    speed: number
    color: Color
  }
  lighting: {
    ambient: Color
    directional: Color
    shadows: boolean
    fogDensity: number
  }
}

// Project System
export interface Project {
  id: string
  name: string
  description: string
  category: 'web' | 'mobile' | 'data' | 'ai' | 'creative' | 'research'
  tags: string[]
  createdDate: Date
  lastUpdated: Date
  status: 'active' | 'completed' | 'archived' | 'planning'
  
  // Growth Data
  growthStage: GrowthStage
  growthMetrics: {
    commits: number
    interactions: number
    timeInvested: number // hours
    complexity: number // 0-1
  }
  
  // Visual Properties
  position: [number, number, number]
  plantType: 'tree' | 'flower' | 'vine' | 'shrub' | 'grass'
  color: Color
  size: number
  
  // Integration Data
  githubData?: {
    url: string
    commits: number
    stars: number
    forks: number
    language: string
  }
  
  analytics: {
    views: number
    interactions: number
    shareCount: number
    timeSpent: number
  }
  
  media: {
    screenshots: string[]
    videos: string[]
    thumbnail: string
  }
}

// Skill System
export interface Skill {
  id: string
  name: string
  category: 'frontend' | 'backend' | 'data' | 'design' | 'tools' | 'soft'
  proficiency: number // 0-1
  experience: number // years
  projects: string[] // project IDs
  keywords: string[]
  
  // Constellation Position
  position: [number, number, number]
  connections: string[] // connected skill IDs
  brightness: number // 0-1
  constellation: string // group name
}

// Visitor & Analytics
export interface VisitorSession {
  id: string
  startTime: Date
  currentPath: string
  interactions: Interaction[]
  device: 'mobile' | 'tablet' | 'desktop'
  preferences: {
    reducedMotion: boolean
    highContrast: boolean
    complexityLevel: ComplexityLevel
  }
}

export interface Interaction {
  type: InteractionType
  target: string // project/skill ID
  timestamp: Date
  duration?: number
  position?: [number, number, number]
  metadata?: Record<string, any>
}

// Real-time Data
export interface RealtimeData {
  activeVisitors: number
  recentInteractions: Interaction[]
  weatherUpdates: WeatherState
  projectGrowthUpdates: {
    projectId: string
    newGrowthStage: GrowthStage
    metrics: Project['growthMetrics']
  }[]
  systemHealth: {
    performance: number // 0-1
    loadTime: number
    errorRate: number
  }
}

// Camera & Navigation
export interface CameraState {
  position: Vector3
  target: Vector3
  mode: 'orbit' | 'fly' | 'focus' | 'cinematic'
  constraints: {
    minDistance: number
    maxDistance: number
    enablePan: boolean
    enableZoom: boolean
    enableRotate: boolean
  }
}

// UI & Interaction State
export interface UIState {
  activeModal: string | null
  selectedProject: Project | null
  selectedSkill: Skill | null
  showingDetails: boolean
  navigationOpen: boolean
  settingsOpen: boolean
  loadingStates: Record<string, boolean>
  notifications: Notification[]
}

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  message: string
  duration: number
  persistent: boolean
}

// Animation & Effects
export interface AnimationConfig {
  duration: number
  easing: string
  delay?: number
  loop?: boolean
  yoyo?: boolean
}

export interface ParticleSystemConfig {
  count: number
  spread: number
  speed: [number, number] // min, max
  size: [number, number] // min, max
  life: [number, number] // min, max seconds
  gravity: number
  color: Color
  opacity: [number, number] // min, max
}

// Store State Interface
export interface GardenState {
  // Core Garden State
  season: Season
  weather: WeatherState
  timeOfDay: TimeOfDay
  
  // User Interaction
  selectedProject: Project | null
  selectedSkill: Skill | null
  navigationMode: NavigationMode
  visitorSession: VisitorSession
  
  // Data
  projects: Project[]
  skills: Skill[]
  realtimeData: RealtimeData
  
  // UI State
  ui: UIState
  camera: CameraState
  
  // Settings
  settings: {
    complexityLevel: ComplexityLevel
    soundEnabled: boolean
    particlesEnabled: boolean
    autoRotate: boolean
    theme: 'auto' | 'light' | 'dark'
  }
  
  // Performance
  performance: {
    fps: number
    renderTime: number
    memoryUsage: number
    isOptimizedMode: boolean
  }
}

// Action Types
export interface GardenActions {
  // Weather & Environment
  updateWeather: (weather: Partial<WeatherState>) => void
  changeSeason: (season: Season) => void
  setTimeOfDay: (time: TimeOfDay) => void
  
  // Project Interactions
  selectProject: (project: Project | null) => void
  updateProjectGrowth: (projectId: string, metrics: Partial<Project['growthMetrics']>) => void
  plantSeed: (position: [number, number, number], projectData: Partial<Project>) => void
  
  // Skill Navigation
  selectSkill: (skill: Skill | null) => void
  updateSkillProficiency: (skillId: string, proficiency: number) => void
  
  // Camera & Navigation
  setCameraMode: (mode: CameraState['mode']) => void
  setCameraPosition: (position: Vector3, target?: Vector3) => void
  setNavigationMode: (mode: NavigationMode) => void
  
  // Real-time Updates
  updateRealtimeData: (data: Partial<RealtimeData>) => void
  trackInteraction: (interaction: Omit<Interaction, 'timestamp'>) => void
  
  // UI Management
  openModal: (modalId: string) => void
  closeModal: () => void
  showNotification: (notification: Omit<Notification, 'id'>) => void
  dismissNotification: (id: string) => void
  
  // Settings
  updateSettings: (settings: Partial<GardenState['settings']>) => void
  setComplexityLevel: (level: ComplexityLevel) => void
  
  // Performance
  updatePerformanceMetrics: (metrics: Partial<GardenState['performance']>) => void
  enableOptimizedMode: () => void
  disableOptimizedMode: () => void
}

// Component Props Interfaces
export interface GardenCanvasProps {
  className?: string
  onProjectSelect?: (project: Project) => void
  onSkillSelect?: (skill: Skill) => void
}

export interface ProjectPlantProps {
  project: Project
  isSelected?: boolean
  onInteract?: (type: InteractionType) => void
  level: ComplexityLevel
}

export interface WeatherSystemProps {
  weather: WeatherState
  enabled: boolean
  intensity?: number
}

export interface SkillConstellationProps {
  skills: Skill[]
  selectedSkill?: Skill | null
  onSkillSelect: (skill: Skill) => void
  visible: boolean
}

export interface CameraControllerProps {
  state: CameraState
  onStateChange: (state: Partial<CameraState>) => void
  autoRotate: boolean
}

// API Response Types
export interface APIResponse<T> {
  success: boolean
  data: T
  error?: string
  timestamp: string
}

export interface WebSocketMessage {
  type: 'weather_update' | 'project_growth' | 'visitor_joined' | 'visitor_left' | 'interaction'
  payload: any
  timestamp: string
}

// Shader Uniform Types
export interface ShaderUniforms {
  time: { value: number }
  season: { value: number } // 0-3 for spring,summer,autumn,winter
  weather: { value: number } // 0-4 for weather moods
  fogDensity: { value: number }
  lightIntensity: { value: number }
  colorPalette: { value: Color[] }
}

// Performance Monitoring
export interface PerformanceMetrics {
  fps: number
  renderTime: number
  geometryCount: number
  materialCount: number
  textureMemory: number
  drawCalls: number
}

export interface LODLevel {
  distance: number
  geometry: 'high' | 'medium' | 'low'
  material: 'full' | 'simplified' | 'impostor'
  animations: boolean
  particles: boolean
}