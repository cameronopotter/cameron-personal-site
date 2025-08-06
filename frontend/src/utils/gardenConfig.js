/**
 * Garden Configuration Settings
 * Central configuration for the digital garden
 */

import { Color } from 'three'

export const GARDEN_CONFIG = {
  // Canvas and Scene Settings
  scene: {
    background: new Color('#0a0a0a'),
    fogColor: new Color('#87CEEB'),
    fogNear: 10,
    fogFar: 100
  },

  // Camera Settings
  camera: {
    fov: 75,
    near: 0.1,
    far: 1000,
    position: [0, 10, 15],
    target: [0, 0, 0]
  },

  // Lighting Configuration
  lighting: {
    ambient: {
      intensity: 0.4,
      color: new Color('#87CEEB')
    },
    directional: {
      intensity: 1.2,
      color: new Color('#FFD54F'),
      position: [10, 20, 10],
      castShadow: true,
      shadowMapSize: 2048
    }
  },

  // Ground Settings
  ground: {
    size: 100,
    segments: 32,
    color: new Color('#2a4a2a'),
    roughness: 0.8,
    metalness: 0.1
  },

  // Project Plant Settings
  plants: {
    maxDistance: 25,
    minDistance: 3,
    heightVariation: 0.5,
    growthAnimationSpeed: 1.5,
    interactionRadius: 2
  },

  // Skill Constellation Settings
  constellation: {
    height: 15,
    radius: 20,
    connectionDistance: 5,
    particleSize: 0.2,
    animationSpeed: 0.5
  },

  // Weather System Settings
  weather: {
    transitionDuration: 3000,
    particleLifetime: 5000,
    intensityMultiplier: 1.0,
    maxParticles: 2000
  },

  // Performance Settings
  performance: {
    lodLevels: [
      { distance: 10, complexity: 4 },
      { distance: 25, complexity: 3 },
      { distance: 50, complexity: 2 },
      { distance: 100, complexity: 1 }
    ],
    targetFrameRate: 60,
    adaptiveQuality: true,
    frustumCulling: true
  },

  // Animation Settings
  animations: {
    plantGrowth: {
      duration: 2000,
      easing: 'easeOutElastic'
    },
    cameraTransition: {
      duration: 1500,
      easing: 'easeInOutCubic'
    },
    weatherTransition: {
      duration: 3000,
      easing: 'easeInOutSine'
    },
    interaction: {
      duration: 300,
      easing: 'easeOutBack'
    }
  },

  // UI Settings
  ui: {
    glassOpacity: 0.1,
    backdropBlur: 20,
    borderRadius: 16,
    notificationDuration: 5000
  },

  // Accessibility Settings
  accessibility: {
    reducedMotionMultiplier: 0.1,
    highContrastMultiplier: 1.5,
    focusRingColor: new Color('#4CAF50'),
    focusRingWidth: 2
  }
}

export const SEASONAL_CONFIGS = {
  spring: {
    primaryColor: new Color('#4CAF50'),
    secondaryColor: new Color('#8BC34A'),
    accentColor: new Color('#2196F3'),
    backgroundColor: new Color('#0a1a0a'),
    ambientLight: new Color('#87CEEB'),
    directionalLight: new Color('#FFD54F'),
    groundColor: new Color('#2a4a2a'),
    particleType: 'sparkles'
  },
  summer: {
    primaryColor: new Color('#2E7D32'),
    secondaryColor: new Color('#FF9800'),
    accentColor: new Color('#9C27B0'),
    backgroundColor: new Color('#0f1a0a'),
    ambientLight: new Color('#FFD54F'),
    directionalLight: new Color('#FF8A65'),
    groundColor: new Color('#1f3f1f'),
    particleType: 'sparkles'
  },
  autumn: {
    primaryColor: new Color('#FFC107'),
    secondaryColor: new Color('#F44336'),
    accentColor: new Color('#FF5722'),
    backgroundColor: new Color('#1a150a'),
    ambientLight: new Color('#FFAB91'),
    directionalLight: new Color('#BCAAA4'),
    groundColor: new Color('#3f2f1f'),
    particleType: 'leaves'
  },
  winter: {
    primaryColor: new Color('#1976D2'),
    secondaryColor: new Color('#9E9E9E'),
    accentColor: new Color('#FAFAFA'),
    backgroundColor: new Color('#0a0f1a'),
    ambientLight: new Color('#B0BEC5'),
    directionalLight: new Color('#263238'),
    groundColor: new Color('#2f3f4f'),
    particleType: 'snow'
  }
}

export const WEATHER_MOODS = {
  sunny: {
    particles: 'sparkles',
    intensity: 0.7,
    ambientMultiplier: 1.2,
    directionalMultiplier: 1.0
  },
  cloudy: {
    particles: 'sparkles',
    intensity: 0.4,
    ambientMultiplier: 0.8,
    directionalMultiplier: 0.7
  },
  rainy: {
    particles: 'rain',
    intensity: 0.9,
    ambientMultiplier: 0.6,
    directionalMultiplier: 0.5
  },
  stormy: {
    particles: 'rain',
    intensity: 1.2,
    ambientMultiplier: 0.4,
    directionalMultiplier: 0.3
  },
  snowy: {
    particles: 'snow',
    intensity: 0.8,
    ambientMultiplier: 0.9,
    directionalMultiplier: 0.6
  },
  aurora: {
    particles: 'aurora',
    intensity: 0.6,
    ambientMultiplier: 0.7,
    directionalMultiplier: 0.4
  }
}

export const COMPLEXITY_LEVELS = {
  1: {
    name: 'Minimal',
    shadows: false,
    particles: false,
    postProcessing: false,
    lodLevel: 1,
    maxParticles: 100
  },
  2: {
    name: 'Low',
    shadows: true,
    particles: true,
    postProcessing: false,
    lodLevel: 2,
    maxParticles: 500
  },
  3: {
    name: 'Medium',
    shadows: true,
    particles: true,
    postProcessing: true,
    lodLevel: 3,
    maxParticles: 1000
  },
  4: {
    name: 'High',
    shadows: true,
    particles: true,
    postProcessing: true,
    lodLevel: 4,
    maxParticles: 2000
  }
}

// Helper functions
export const getSeasonalConfig = (season) => {
  return SEASONAL_CONFIGS[season] || SEASONAL_CONFIGS.spring
}

export const getWeatherConfig = (mood) => {
  return WEATHER_MOODS[mood] || WEATHER_MOODS.sunny
}

export const getComplexityConfig = (level) => {
  return COMPLEXITY_LEVELS[level] || COMPLEXITY_LEVELS[3]
}

export const calculateOptimalComplexity = (fps, targetFps = 60) => {
  if (fps >= targetFps * 0.9) return 4
  if (fps >= targetFps * 0.7) return 3
  if (fps >= targetFps * 0.5) return 2
  return 1
}

export const getResponsiveSettings = () => {
  const isMobile = window.innerWidth < 768
  const isTablet = window.innerWidth < 1024 && window.innerWidth >= 768
  
  if (isMobile) {
    return {
      maxComplexity: 2,
      targetFps: 30,
      maxParticles: 500
    }
  }
  
  if (isTablet) {
    return {
      maxComplexity: 3,
      targetFps: 45,
      maxParticles: 1000
    }
  }
  
  return {
    maxComplexity: 4,
    targetFps: 60,
    maxParticles: 2000
  }
}

export default GARDEN_CONFIG