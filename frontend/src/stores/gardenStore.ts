import { create } from 'zustand'
import { devtools, subscribeWithSelector } from 'zustand/middleware'
import { Vector3, Color } from 'three'
import type { 
  GardenState, 
  GardenActions, 
  Project, 
  Skill, 
  WeatherState, 
  Season,
  TimeOfDay,
  NavigationMode,
  ComplexityLevel,
  Interaction,
  RealtimeData,
  VisitorSession,
  Notification
} from '@/types'

// Default state values
const createDefaultWeather = (): WeatherState => ({
  mood: 'sunny',
  intensity: 0.7,
  timeOfDay: 'day',
  seasonalInfluence: 0.5,
  particles: {
    type: 'sparkles',
    density: 0.3,
    speed: 0.5,
    color: new Color('#4CAF50')
  },
  lighting: {
    ambient: new Color('#87CEEB'),
    directional: new Color('#FFD54F'),
    shadows: true,
    fogDensity: 0.01
  }
})

const createDefaultVisitorSession = (): VisitorSession => ({
  id: crypto.randomUUID(),
  startTime: new Date(),
  currentPath: '/',
  interactions: [],
  device: getDeviceType(),
  preferences: {
    reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    highContrast: window.matchMedia('(prefers-contrast: high)').matches,
    complexityLevel: 3
  }
})

const createDefaultProjects = (): Project[] => [
  {
    id: 'digital-greenhouse',
    name: 'Digital Greenhouse',
    description: 'An immersive 3D portfolio garden that grows with real data',
    category: 'web',
    tags: ['React', 'Three.js', 'TypeScript', 'WebGL'],
    createdDate: new Date('2024-01-15'),
    lastUpdated: new Date(),
    status: 'active',
    growthStage: 'blooming',
    growthMetrics: {
      commits: 142,
      interactions: 89,
      timeInvested: 320,
      complexity: 0.9
    },
    position: [0, 0, 0],
    plantType: 'tree',
    color: new Color('#4CAF50'),
    size: 1.5,
    githubData: {
      url: 'https://github.com/cameronopotter/digital-greenhouse',
      commits: 142,
      stars: 23,
      forks: 4,
      language: 'TypeScript'
    },
    analytics: {
      views: 256,
      interactions: 89,
      shareCount: 12,
      timeSpent: 1420
    },
    media: {
      screenshots: ['/images/greenhouse-1.jpg', '/images/greenhouse-2.jpg'],
      videos: ['/videos/greenhouse-demo.mp4'],
      thumbnail: '/images/greenhouse-thumb.jpg'
    }
  },
  {
    id: 'ai-poetry-generator',
    name: 'AI Poetry Generator',
    description: 'Neural network that generates poetry in various styles',
    category: 'ai',
    tags: ['Python', 'TensorFlow', 'NLP', 'Poetry'],
    createdDate: new Date('2023-08-22'),
    lastUpdated: new Date('2024-01-10'),
    status: 'completed',
    growthStage: 'mature',
    growthMetrics: {
      commits: 87,
      interactions: 45,
      timeInvested: 180,
      complexity: 0.7
    },
    position: [-5, 0, 3],
    plantType: 'flower',
    color: new Color('#9C27B0'),
    size: 1.2,
    analytics: {
      views: 189,
      interactions: 45,
      shareCount: 8,
      timeSpent: 890
    },
    media: {
      screenshots: ['/images/poetry-1.jpg'],
      videos: [],
      thumbnail: '/images/poetry-thumb.jpg'
    }
  },
  {
    id: 'responsive-dashboard',
    name: 'Responsive Dashboard',
    description: 'Modern dashboard with real-time data visualization',
    category: 'web',
    tags: ['React', 'D3.js', 'Material-UI', 'Charts'],
    createdDate: new Date('2023-11-05'),
    lastUpdated: new Date('2024-01-20'),
    status: 'active',
    growthStage: 'growing',
    growthMetrics: {
      commits: 64,
      interactions: 32,
      timeInvested: 120,
      complexity: 0.6
    },
    position: [4, 0, -2],
    plantType: 'shrub',
    color: new Color('#2196F3'),
    size: 1.0,
    analytics: {
      views: 134,
      interactions: 32,
      shareCount: 6,
      timeSpent: 720
    },
    media: {
      screenshots: ['/images/dashboard-1.jpg', '/images/dashboard-2.jpg'],
      videos: ['/videos/dashboard-demo.mp4'],
      thumbnail: '/images/dashboard-thumb.jpg'
    }
  }
]

const createDefaultSkills = (): Skill[] => [
  {
    id: 'react',
    name: 'React',
    category: 'frontend',
    proficiency: 0.95,
    experience: 4,
    projects: ['digital-greenhouse', 'responsive-dashboard'],
    keywords: ['hooks', 'context', 'jsx', 'virtual-dom'],
    position: [0, 5, 0],
    connections: ['typescript', 'javascript', 'html', 'css'],
    brightness: 0.95,
    constellation: 'frontend'
  },
  {
    id: 'typescript',
    name: 'TypeScript',
    category: 'frontend',
    proficiency: 0.9,
    experience: 3,
    projects: ['digital-greenhouse'],
    keywords: ['types', 'interfaces', 'generics', 'strict'],
    position: [2, 4, 1],
    connections: ['react', 'javascript', 'node'],
    brightness: 0.9,
    constellation: 'frontend'
  },
  {
    id: 'threejs',
    name: 'Three.js',
    category: 'frontend',
    proficiency: 0.8,
    experience: 2,
    projects: ['digital-greenhouse'],
    keywords: ['webgl', '3d', 'shaders', 'geometry'],
    position: [-2, 3, 2],
    connections: ['javascript', 'glsl'],
    brightness: 0.8,
    constellation: 'graphics'
  },
  {
    id: 'python',
    name: 'Python',
    category: 'backend',
    proficiency: 0.85,
    experience: 5,
    projects: ['ai-poetry-generator'],
    keywords: ['machine-learning', 'data-science', 'automation'],
    position: [1, -2, -3],
    connections: ['tensorflow', 'pandas', 'numpy'],
    brightness: 0.85,
    constellation: 'backend'
  }
]

// Store implementation
export interface GardenStore extends GardenState, GardenActions {}

export const useGardenStore = create<GardenStore>()(
  devtools(
    subscribeWithSelector(
      (set, get) => ({
        // Initial State
        season: 'spring',
        weather: createDefaultWeather(),
        timeOfDay: 'day',
        selectedProject: null,
        selectedSkill: null,
        navigationMode: 'explore',
        visitorSession: createDefaultVisitorSession(),
        projects: createDefaultProjects(),
        skills: createDefaultSkills(),
        realtimeData: {
          activeVisitors: 1,
          recentInteractions: [],
          weatherUpdates: createDefaultWeather(),
          projectGrowthUpdates: [],
          systemHealth: {
            performance: 0.95,
            loadTime: 1200,
            errorRate: 0.01
          }
        },
        ui: {
          activeModal: null,
          selectedProject: null,
          selectedSkill: null,
          showingDetails: false,
          navigationOpen: false,
          settingsOpen: false,
          loadingStates: {},
          notifications: []
        },
        camera: {
          position: new Vector3(0, 10, 15),
          target: new Vector3(0, 0, 0),
          mode: 'orbit',
          constraints: {
            minDistance: 5,
            maxDistance: 50,
            enablePan: true,
            enableZoom: true,
            enableRotate: true
          }
        },
        settings: {
          complexityLevel: 3,
          soundEnabled: true,
          particlesEnabled: true,
          autoRotate: true,
          theme: 'auto'
        },
        performance: {
          fps: 60,
          renderTime: 16.67,
          memoryUsage: 0,
          isOptimizedMode: false
        },

        // Weather & Environment Actions
        updateWeather: (weatherUpdate) => {
          set((state) => ({
            weather: { ...state.weather, ...weatherUpdate }
          }))
        },

        changeSeason: (season) => {
          set(() => ({ season }))
          
          // Update weather based on season
          const seasonalWeather: Record<Season, Partial<WeatherState>> = {
            spring: {
              mood: 'sunny',
              particles: { type: 'sparkles', density: 0.4, speed: 0.3, color: new Color('#8BC34A') },
              lighting: { ambient: new Color('#87CEEB'), directional: new Color('#FFD54F') }
            },
            summer: {
              mood: 'sunny',
              particles: { type: 'sparkles', density: 0.6, speed: 0.5, color: new Color('#FF9800') },
              lighting: { ambient: new Color('#FFD54F'), directional: new Color('#FF8A65') }
            },
            autumn: {
              mood: 'cloudy',
              particles: { type: 'leaves', density: 0.5, speed: 0.7, color: new Color('#FF5722') },
              lighting: { ambient: new Color('#FFAB91'), directional: new Color('#BCAAA4') }
            },
            winter: {
              mood: 'starry',
              particles: { type: 'snow', density: 0.3, speed: 0.2, color: new Color('#FAFAFA') },
              lighting: { ambient: new Color('#B0BEC5'), directional: new Color('#263238') }
            }
          }
          
          get().updateWeather(seasonalWeather[season])
        },

        setTimeOfDay: (timeOfDay) => {
          set(() => ({ timeOfDay }))
          
          // Update lighting based on time of day
          const timeBasedLighting: Record<TimeOfDay, Partial<WeatherState['lighting']>> = {
            dawn: { ambient: new Color('#FFB74D'), directional: new Color('#FF8A65') },
            day: { ambient: new Color('#87CEEB'), directional: new Color('#FFD54F') },
            dusk: { ambient: new Color('#FF8A65'), directional: new Color('#FF5722') },
            night: { ambient: new Color('#263238'), directional: new Color('#37474F') }
          }
          
          get().updateWeather({ lighting: timeBasedLighting[timeOfDay] })
        },

        // Project Actions
        selectProject: (project) => {
          set((state) => ({ 
            selectedProject: project,
            ui: { ...state.ui, selectedProject: project }
          }))
          
          if (project) {
            get().trackInteraction({
              type: 'click',
              target: project.id,
              metadata: { projectName: project.name, category: project.category }
            })
          }
        },

        updateProjectGrowth: (projectId, metrics) => {
          set((state) => ({
            projects: state.projects.map(project =>
              project.id === projectId
                ? {
                    ...project,
                    growthMetrics: { ...project.growthMetrics, ...metrics },
                    growthStage: calculateGrowthStage({ ...project.growthMetrics, ...metrics })
                  }
                : project
            )
          }))
        },

        plantSeed: (position, projectData) => {
          const newProject: Project = {
            id: crypto.randomUUID(),
            name: projectData.name || 'New Project',
            description: projectData.description || '',
            category: projectData.category || 'web',
            tags: projectData.tags || [],
            createdDate: new Date(),
            lastUpdated: new Date(),
            status: 'planning',
            growthStage: 'seed',
            growthMetrics: {
              commits: 0,
              interactions: 0,
              timeInvested: 0,
              complexity: 0
            },
            position,
            plantType: 'flower',
            color: new Color('#4CAF50'),
            size: 0.1,
            analytics: {
              views: 0,
              interactions: 0,
              shareCount: 0,
              timeSpent: 0
            },
            media: {
              screenshots: [],
              videos: [],
              thumbnail: ''
            }
          }
          
          set((state) => ({
            projects: [...state.projects, newProject]
          }))
          
          get().trackInteraction({
            type: 'click',
            target: 'seed-planting',
            position,
            metadata: { newProjectId: newProject.id }
          })
        },

        // Skill Actions
        selectSkill: (skill) => {
          set((state) => ({ 
            selectedSkill: skill,
            ui: { ...state.ui, selectedSkill: skill }
          }))
          
          if (skill) {
            get().trackInteraction({
              type: 'click',
              target: skill.id,
              metadata: { skillName: skill.name, proficiency: skill.proficiency }
            })
          }
        },

        updateSkillProficiency: (skillId, proficiency) => {
          set((state) => ({
            skills: state.skills.map(skill =>
              skill.id === skillId
                ? { ...skill, proficiency, brightness: proficiency }
                : skill
            )
          }))
        },

        // Camera & Navigation Actions
        setCameraMode: (mode) => {
          set((state) => ({
            camera: { ...state.camera, mode }
          }))
        },

        setCameraPosition: (position, target) => {
          set((state) => ({
            camera: { 
              ...state.camera, 
              position,
              target: target || state.camera.target
            }
          }))
        },

        setNavigationMode: (mode) => {
          set(() => ({ navigationMode: mode }))
          
          get().trackInteraction({
            type: 'click',
            target: 'navigation-mode',
            metadata: { mode }
          })
        },

        // Real-time Data Actions
        updateRealtimeData: (data) => {
          set((state) => ({
            realtimeData: { ...state.realtimeData, ...data }
          }))
        },

        trackInteraction: (interaction) => {
          const fullInteraction: Interaction = {
            ...interaction,
            timestamp: new Date()
          }
          
          set((state) => ({
            visitorSession: {
              ...state.visitorSession,
              interactions: [...state.visitorSession.interactions, fullInteraction]
            },
            realtimeData: {
              ...state.realtimeData,
              recentInteractions: [
                fullInteraction,
                ...state.realtimeData.recentInteractions.slice(0, 9)
              ]
            }
          }))
        },

        // UI Management Actions
        openModal: (modalId) => {
          set((state) => ({
            ui: { ...state.ui, activeModal: modalId }
          }))
        },

        closeModal: () => {
          set((state) => ({
            ui: { ...state.ui, activeModal: null }
          }))
        },

        showNotification: (notification) => {
          const fullNotification: Notification = {
            ...notification,
            id: crypto.randomUUID()
          }
          
          set((state) => ({
            ui: {
              ...state.ui,
              notifications: [...state.ui.notifications, fullNotification]
            }
          }))
          
          // Auto-dismiss non-persistent notifications
          if (!notification.persistent && notification.duration) {
            setTimeout(() => {
              get().dismissNotification(fullNotification.id)
            }, notification.duration)
          }
        },

        dismissNotification: (id) => {
          set((state) => ({
            ui: {
              ...state.ui,
              notifications: state.ui.notifications.filter(n => n.id !== id)
            }
          }))
        },

        // Settings Actions
        updateSettings: (settings) => {
          set((state) => ({
            settings: { ...state.settings, ...settings }
          }))
        },

        setComplexityLevel: (level) => {
          set((state) => ({
            settings: { ...state.settings, complexityLevel: level }
          }))
        },

        // Performance Actions
        updatePerformanceMetrics: (metrics) => {
          set((state) => ({
            performance: { ...state.performance, ...metrics }
          }))
        },

        enableOptimizedMode: () => {
          set((state) => ({
            performance: { ...state.performance, isOptimizedMode: true },
            settings: { 
              ...state.settings, 
              complexityLevel: Math.max(1, state.settings.complexityLevel - 1) as ComplexityLevel,
              particlesEnabled: false
            }
          }))
        },

        disableOptimizedMode: () => {
          set((state) => ({
            performance: { ...state.performance, isOptimizedMode: false }
          }))
        },

        // Utility method to initialize with defaults (used in App.tsx)
        initializeWithDefaults: () => {
          // Already initialized with defaults in create()
          get().trackInteraction({
            type: 'focus',
            target: 'garden-initialized',
            metadata: { timestamp: Date.now() }
          })
        }
      }),
      {
        name: 'garden-store'
      }
    ),
    {
      name: 'garden-store'
    }
  )
)

// Helper Functions
function getDeviceType(): 'mobile' | 'tablet' | 'desktop' {
  const width = window.innerWidth
  if (width < 768) return 'mobile'
  if (width < 1024) return 'tablet'
  return 'desktop'
}

function calculateGrowthStage(metrics: Project['growthMetrics']): Project['growthStage'] {
  const { commits, interactions, timeInvested, complexity } = metrics
  
  // Weighted score calculation
  const score = (
    (commits * 0.3) + 
    (interactions * 0.2) + 
    (timeInvested * 0.001) + 
    (complexity * 100 * 0.5)
  )
  
  if (score < 5) return 'seed'
  if (score < 15) return 'sprout'
  if (score < 40) return 'growing'
  if (score < 80) return 'blooming'
  return 'mature'
}

// Selectors for optimized re-renders
export const useProjectsSelector = () => useGardenStore((state) => state.projects)
export const useSkillsSelector = () => useGardenStore((state) => state.skills)
export const useWeatherSelector = () => useGardenStore((state) => state.weather)
export const useSelectedProjectSelector = () => useGardenStore((state) => state.selectedProject)
export const useSelectedSkillSelector = () => useGardenStore((state) => state.selectedSkill)
export const useUISelector = () => useGardenStore((state) => state.ui)
export const useSettingsSelector = () => useGardenStore((state) => state.settings)
export const usePerformanceSelector = () => useGardenStore((state) => state.performance)