/**
 * API Service Layer for Digital Greenhouse
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000/api/v1'
const WS_URL = 'ws://localhost:8000/ws/garden'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
    this.wsURL = WS_URL
    this.cache = new Map()
    this.cacheTimeout = 5 * 60 * 1000 // 5 minutes
  }

  // Generic fetch wrapper with error handling
  async fetchWithRetry(url, options = {}, retries = 3) {
    const fullUrl = url.startsWith('http') ? url : `${this.baseURL}${url}`
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers
      },
      credentials: 'include',
      ...options
    }

    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(fullUrl, defaultOptions)
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        return data
      } catch (error) {
        console.warn(`API request failed (attempt ${i + 1}/${retries}):`, error)
        
        if (i === retries - 1) {
          throw error
        }
        
        // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000))
      }
    }
  }

  // Cache management
  getCachedData(key) {
    const cached = this.cache.get(key)
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data
    }
    this.cache.delete(key)
    return null
  }

  setCachedData(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  // Garden State API
  async getGardenState() {
    const cacheKey = 'garden_state'
    const cached = this.getCachedData(cacheKey)
    if (cached) return cached

    try {
      const data = await this.fetchWithRetry('/garden')
      this.setCachedData(cacheKey, data)
      return data
    } catch (error) {
      console.warn('Failed to fetch garden state:', error)
      return this.getDefaultGardenState()
    }
  }

  async updateGardenState(updates) {
    try {
      const data = await this.fetchWithRetry('/garden', {
        method: 'PUT',
        body: JSON.stringify(updates)
      })
      
      // Invalidate cache
      this.cache.delete('garden_state')
      return data
    } catch (error) {
      console.error('Failed to update garden state:', error)
      throw error
    }
  }

  // Projects API
  async getProjects() {
    const cacheKey = 'projects'
    const cached = this.getCachedData(cacheKey)
    if (cached) return cached

    try {
      const data = await this.fetchWithRetry('/projects')
      this.setCachedData(cacheKey, data)
      return data
    } catch (error) {
      console.warn('Failed to fetch projects:', error)
      return []
    }
  }

  async getProjectDetails(projectId) {
    try {
      const data = await this.fetchWithRetry(`/projects/${projectId}`)
      return data
    } catch (error) {
      console.error('Failed to fetch project details:', error)
      throw error
    }
  }

  async updateProjectGrowth(projectId, metrics) {
    try {
      const data = await this.fetchWithRetry(`/projects/${projectId}/growth`, {
        method: 'PUT',
        body: JSON.stringify(metrics)
      })
      
      // Invalidate projects cache
      this.cache.delete('projects')
      return data
    } catch (error) {
      console.error('Failed to update project growth:', error)
      throw error
    }
  }

  async createProject(projectData) {
    try {
      const data = await this.fetchWithRetry('/projects', {
        method: 'POST',
        body: JSON.stringify(projectData)
      })
      
      // Invalidate projects cache
      this.cache.delete('projects')
      return data
    } catch (error) {
      console.error('Failed to create project:', error)
      throw error
    }
  }

  // Skills API
  async getSkills() {
    const cacheKey = 'skills'
    const cached = this.getCachedData(cacheKey)
    if (cached) return cached

    try {
      const data = await this.fetchWithRetry('/skills')
      this.setCachedData(cacheKey, data)
      return data
    } catch (error) {
      console.warn('Failed to fetch skills:', error)
      return []
    }
  }

  async updateSkillProficiency(skillId, proficiency) {
    try {
      const data = await this.fetchWithRetry(`/skills/${skillId}`, {
        method: 'PUT',
        body: JSON.stringify({ proficiency })
      })
      
      // Invalidate skills cache
      this.cache.delete('skills')
      return data
    } catch (error) {
      console.error('Failed to update skill proficiency:', error)
      throw error
    }
  }

  // Weather API
  async getWeather() {
    const cacheKey = 'weather'
    const cached = this.getCachedData(cacheKey)
    if (cached) return cached

    try {
      const data = await this.fetchWithRetry('/weather')
      this.setCachedData(cacheKey, data)
      return data
    } catch (error) {
      console.warn('Failed to fetch weather:', error)
      return this.getDefaultWeather()
    }
  }

  async updateWeather(weatherData) {
    try {
      const data = await this.fetchWithRetry('/weather', {
        method: 'PUT',
        body: JSON.stringify(weatherData)
      })
      
      // Invalidate weather cache
      this.cache.delete('weather')
      return data
    } catch (error) {
      console.error('Failed to update weather:', error)
      throw error
    }
  }

  // Analytics API
  async trackInteraction(interaction) {
    try {
      const data = await this.fetchWithRetry('/analytics/interactions', {
        method: 'POST',
        body: JSON.stringify(interaction)
      })
      return data
    } catch (error) {
      console.warn('Failed to track interaction:', error)
      // Don't throw - analytics failures shouldn't break the app
    }
  }

  async getAnalytics(timeRange = '24h') {
    const cacheKey = `analytics_${timeRange}`
    const cached = this.getCachedData(cacheKey)
    if (cached) return cached

    try {
      const data = await this.fetchWithRetry(`/analytics?range=${timeRange}`)
      this.setCachedData(cacheKey, data)
      return data
    } catch (error) {
      console.warn('Failed to fetch analytics:', error)
      return {
        interactions: [],
        visitors: 0,
        pageViews: 0,
        averageSessionTime: 0
      }
    }
  }

  // Visitors API
  async trackVisitor(visitorData) {
    try {
      const data = await this.fetchWithRetry('/visitors', {
        method: 'POST',
        body: JSON.stringify(visitorData)
      })
      return data
    } catch (error) {
      console.warn('Failed to track visitor:', error)
    }
  }

  async getVisitorStats() {
    try {
      const data = await this.fetchWithRetry('/visitors/stats')
      return data
    } catch (error) {
      console.warn('Failed to fetch visitor stats:', error)
      return {
        activeVisitors: 1,
        totalVisitors: 0,
        uniqueVisitors: 0
      }
    }
  }

  // Integration APIs
  async syncGitHubData() {
    try {
      const data = await this.fetchWithRetry('/integrations/github/sync', {
        method: 'POST'
      })
      
      // Invalidate related caches
      this.cache.delete('projects')
      this.cache.delete('garden_state')
      return data
    } catch (error) {
      console.error('Failed to sync GitHub data:', error)
      throw error
    }
  }

  async getIntegrationStatus() {
    try {
      const data = await this.fetchWithRetry('/integrations/status')
      return data
    } catch (error) {
      console.warn('Failed to fetch integration status:', error)
      return {
        github: { connected: false, lastSync: null },
        spotify: { connected: false, lastSync: null },
        wakatime: { connected: false, lastSync: null }
      }
    }
  }

  // WebSocket Management
  createWebSocket(onMessage, onError, onClose) {
    try {
      const ws = new WebSocket(this.wsURL)
      
      ws.onopen = () => {
        console.log('WebSocket connected')
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage(data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        onError && onError(error)
      }
      
      ws.onclose = () => {
        console.log('WebSocket disconnected')
        onClose && onClose()
      }
      
      return ws
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      onError && onError(error)
      return null
    }
  }

  // Default/Fallback Data
  getDefaultGardenState() {
    return {
      season: 'spring',
      weather: this.getDefaultWeather(),
      projects: [],
      skills: [],
      activeVisitors: 1,
      systemHealth: {
        performance: 0.95,
        loadTime: 1200,
        errorRate: 0.01
      }
    }
  }

  getDefaultWeather() {
    return {
      mood: 'sunny',
      intensity: 0.7,
      timeOfDay: 'day',
      seasonalInfluence: 0.5,
      particles: {
        type: 'sparkles',
        density: 0.3,
        speed: 0.5,
        color: '#4CAF50'
      },
      lighting: {
        ambient: '#87CEEB',
        directional: '#FFD54F',
        shadows: true,
        fogDensity: 0.01
      }
    }
  }

  // Utility Methods
  clearCache() {
    this.cache.clear()
  }

  isOnline() {
    return navigator.onLine
  }

  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/health`, {
        method: 'GET',
        timeout: 5000
      })
      return response.ok
    } catch (error) {
      return false
    }
  }
}

// Create singleton instance
export const apiService = new ApiService()

// Export for testing
export { ApiService }

// Convenience functions
export const api = {
  garden: {
    get: () => apiService.getGardenState(),
    update: (data) => apiService.updateGardenState(data)
  },
  projects: {
    list: () => apiService.getProjects(),
    get: (id) => apiService.getProjectDetails(id),
    create: (data) => apiService.createProject(data),
    updateGrowth: (id, metrics) => apiService.updateProjectGrowth(id, metrics)
  },
  skills: {
    list: () => apiService.getSkills(),
    update: (id, proficiency) => apiService.updateSkillProficiency(id, proficiency)
  },
  weather: {
    get: () => apiService.getWeather(),
    update: (data) => apiService.updateWeather(data)
  },
  analytics: {
    track: (interaction) => apiService.trackInteraction(interaction),
    get: (range) => apiService.getAnalytics(range)
  },
  visitors: {
    track: (data) => apiService.trackVisitor(data),
    stats: () => apiService.getVisitorStats()
  },
  integrations: {
    syncGitHub: () => apiService.syncGitHubData(),
    status: () => apiService.getIntegrationStatus()
  }
}

export default apiService