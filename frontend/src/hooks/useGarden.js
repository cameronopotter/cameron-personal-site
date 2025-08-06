/**
 * useGarden Hook
 * Provides high-level garden functionality and state management
 */

import { useEffect, useCallback, useMemo } from 'react'
import { useGardenStore } from '../stores/gardenStore'
import { apiService } from '../services/api'
import { calculateGrowthStage, getPlantTypeForCategory } from '../utils/plantTypes'
import { getSeasonalConfig, getWeatherConfig, calculateOptimalComplexity } from '../utils/gardenConfig'

export const useGarden = () => {
  const {
    // State
    season,
    weather,
    projects,
    skills,
    selectedProject,
    selectedSkill,
    navigationMode,
    settings,
    performance,
    ui,
    visitorSession,
    realtimeData,
    
    // Actions
    changeSeason,
    updateWeather,
    selectProject,
    selectSkill,
    updateProjectGrowth,
    plantSeed,
    setNavigationMode,
    trackInteraction,
    updatePerformanceMetrics,
    setComplexityLevel,
    showNotification
  } = useGardenStore()

  // Computed values
  const isLoading = useMemo(() => {
    return Object.values(ui.loadingStates).some(Boolean)
  }, [ui.loadingStates])

  const activeProjects = useMemo(() => {
    return projects.filter(project => project.status === 'active')
  }, [projects])

  const projectsByGrowthStage = useMemo(() => {
    return projects.reduce((acc, project) => {
      if (!acc[project.growthStage]) {
        acc[project.growthStage] = []
      }
      acc[project.growthStage].push(project)
      return acc
    }, {})
  }, [projects])

  const topSkills = useMemo(() => {
    return skills
      .sort((a, b) => b.proficiency - a.proficiency)
      .slice(0, 10)
  }, [skills])

  const gardenStats = useMemo(() => {
    const totalCommits = projects.reduce((sum, p) => sum + p.growthMetrics.commits, 0)
    const totalInteractions = projects.reduce((sum, p) => sum + p.growthMetrics.interactions, 0)
    const totalTimeInvested = projects.reduce((sum, p) => sum + p.growthMetrics.timeInvested, 0)
    const avgComplexity = projects.length > 0 
      ? projects.reduce((sum, p) => sum + p.growthMetrics.complexity, 0) / projects.length
      : 0

    return {
      totalProjects: projects.length,
      activeProjects: activeProjects.length,
      totalCommits,
      totalInteractions,
      totalTimeInvested,
      avgComplexity,
      totalSkills: skills.length,
      avgSkillProficiency: skills.length > 0 
        ? skills.reduce((sum, s) => sum + s.proficiency, 0) / skills.length
        : 0
    }
  }, [projects, activeProjects, skills])

  // Garden initialization
  const initializeGarden = useCallback(async () => {
    try {
      // Load garden data from API
      const gardenData = await apiService.getGardenState()
      
      if (gardenData) {
        // Update weather if different
        if (gardenData.weather && weather.mood !== gardenData.weather.mood) {
          updateWeather(gardenData.weather)
        }

        // Update season if different
        if (gardenData.season && season !== gardenData.season) {
          changeSeason(gardenData.season)
        }

        showNotification({
          type: 'success',
          title: 'Garden Synchronized',
          message: `Loaded ${gardenData.projects?.length || 0} projects and ${gardenData.skills?.length || 0} skills`,
          duration: 3000
        })
      }
    } catch (error) {
      console.warn('Failed to initialize garden from API:', error)
      showNotification({
        type: 'warning',
        title: 'Garden Ready',
        message: 'Running with local data - some features may be limited',
        duration: 5000
      })
    }
  }, [weather.mood, season, updateWeather, changeSeason, showNotification])

  // Project management
  const createProject = useCallback(async (projectData) => {
    try {
      const position = [
        (Math.random() - 0.5) * 40,
        0,
        (Math.random() - 0.5) * 40
      ]

      const plantType = getPlantTypeForCategory(projectData.category)
      const newProject = await apiService.createProject({
        ...projectData,
        plantType,
        position,
        color: projectData.color || '#4CAF50',
        size: 0.1,
        growthStage: 'seed',
        growthMetrics: {
          commits: 0,
          interactions: 0,
          timeInvested: 0,
          complexity: 0
        }
      })

      plantSeed(position, newProject)
      
      trackInteraction({
        type: 'click',
        target: 'project-created',
        metadata: { projectId: newProject.id, plantType }
      })

      showNotification({
        type: 'success',
        title: 'Project Planted',
        message: `${newProject.name} has been planted as a ${plantType}!`,
        duration: 4000
      })

      return newProject
    } catch (error) {
      console.error('Failed to create project:', error)
      showNotification({
        type: 'error',
        title: 'Planting Failed',
        message: 'Could not create the project. Please try again.',
        duration: 5000
      })
      throw error
    }
  }, [plantSeed, trackInteraction, showNotification])

  const growProject = useCallback(async (projectId, metrics) => {
    try {
      const updatedMetrics = await apiService.updateProjectGrowth(projectId, metrics)
      const newGrowthStage = calculateGrowthStage(updatedMetrics)
      
      updateProjectGrowth(projectId, {
        ...updatedMetrics,
        growthStage: newGrowthStage
      })

      const project = projects.find(p => p.id === projectId)
      if (project && project.growthStage !== newGrowthStage) {
        showNotification({
          type: 'success',
          title: 'Growth Milestone!',
          message: `${project.name} has evolved to ${newGrowthStage} stage!`,
          duration: 4000
        })
      }

      trackInteraction({
        type: 'click',
        target: 'project-growth',
        metadata: { projectId, oldStage: project?.growthStage, newStage: newGrowthStage }
      })

    } catch (error) {
      console.error('Failed to update project growth:', error)
    }
  }, [projects, updateProjectGrowth, showNotification, trackInteraction])

  // Weather and season management
  const changeWeather = useCallback(async (mood) => {
    try {
      const weatherConfig = getWeatherConfig(mood)
      await apiService.updateWeather({ ...weather, mood, ...weatherConfig })
      
      updateWeather({ mood, ...weatherConfig })
      
      trackInteraction({
        type: 'click',
        target: 'weather-change',
        metadata: { newMood: mood, previousMood: weather.mood }
      })

      showNotification({
        type: 'info',
        title: 'Weather Changed',
        message: `The garden atmosphere has shifted to ${mood}`,
        duration: 3000
      })
    } catch (error) {
      console.error('Failed to change weather:', error)
    }
  }, [weather, updateWeather, trackInteraction, showNotification])

  const changeSeason = useCallback(async (newSeason) => {
    try {
      const seasonalConfig = getSeasonalConfig(newSeason)
      changeSeason(newSeason)
      
      // Update weather to match season
      updateWeather({
        ...weather,
        particles: { ...weather.particles, type: seasonalConfig.particleType },
        lighting: {
          ...weather.lighting,
          ambient: seasonalConfig.ambientLight,
          directional: seasonalConfig.directionalLight
        }
      })

      trackInteraction({
        type: 'click',
        target: 'season-change',
        metadata: { newSeason, previousSeason: season }
      })

      showNotification({
        type: 'success',
        title: 'Season Changed',
        message: `Welcome to ${newSeason}! The garden is transforming...`,
        duration: 4000
      })
    } catch (error) {
      console.error('Failed to change season:', error)
    }
  }, [season, weather, changeSeason, updateWeather, trackInteraction, showNotification])

  // Performance optimization
  const optimizePerformance = useCallback(() => {
    const optimalComplexity = calculateOptimalComplexity(performance.fps)
    
    if (optimalComplexity !== settings.complexityLevel) {
      setComplexityLevel(optimalComplexity)
      
      showNotification({
        type: 'info',
        title: 'Performance Optimized',
        message: `Adjusted quality to ${optimalComplexity}/4 for better performance`,
        duration: 3000
      })
    }
  }, [performance.fps, settings.complexityLevel, setComplexityLevel, showNotification])

  // Navigation helpers
  const focusOnProject = useCallback((project) => {
    selectProject(project)
    setNavigationMode('focus')
    
    trackInteraction({
      type: 'click',
      target: 'project-focus',
      metadata: { projectId: project.id, projectName: project.name }
    })
  }, [selectProject, setNavigationMode, trackInteraction])

  const exploreGarden = useCallback(() => {
    selectProject(null)
    selectSkill(null)
    setNavigationMode('explore')
    
    trackInteraction({
      type: 'click',
      target: 'explore-mode'
    })
  }, [selectProject, selectSkill, setNavigationMode, trackInteraction])

  // Auto-sync with backend periodically
  useEffect(() => {
    const syncInterval = setInterval(async () => {
      try {
        const gardenData = await apiService.getGardenState()
        if (gardenData && gardenData.weather) {
          updateWeather(gardenData.weather)
        }
      } catch (error) {
        // Silently fail for periodic syncs
      }
    }, 60000) // Every minute

    return () => clearInterval(syncInterval)
  }, [updateWeather])

  // Performance monitoring
  useEffect(() => {
    if (settings.complexityLevel > 2 && performance.fps < 45) {
      optimizePerformance()
    }
  }, [performance.fps, settings.complexityLevel, optimizePerformance])

  return {
    // State
    season,
    weather,
    projects,
    skills,
    selectedProject,
    selectedSkill,
    navigationMode,
    settings,
    performance,
    ui,
    isLoading,
    
    // Computed values
    activeProjects,
    projectsByGrowthStage,
    topSkills,
    gardenStats,
    
    // Actions
    initializeGarden,
    createProject,
    growProject,
    changeWeather,
    changeSeason,
    focusOnProject,
    exploreGarden,
    selectProject,
    selectSkill,
    trackInteraction,
    optimizePerformance
  }
}

export default useGarden