/**
 * Plant Type Definitions
 * Defines different plant types and their characteristics for projects
 */

import { Color } from 'three'

export const PLANT_TYPES = {
  // Tree - Major projects, established applications
  tree: {
    name: 'Tree',
    description: 'Major projects with significant complexity and impact',
    baseScale: 1.0,
    growthRate: 1.2,
    maxHeight: 3.0,
    categories: ['web', 'desktop', 'backend'],
    characteristics: {
      trunk: {
        radius: [0.1, 0.15],
        height: 1.0,
        color: new Color('#8D6E63'),
        material: { roughness: 0.8, metalness: 0.1 }
      },
      canopy: {
        radius: 0.8,
        height: 1.2,
        segments: 16,
        material: { roughness: 0.6, metalness: 0.2 }
      },
      leaves: {
        count: 3,
        radius: 0.6,
        height: 1.2,
        distribution: 'circular'
      }
    },
    animations: {
      sway: { amplitude: 0.02, frequency: 0.5 },
      breathe: { amplitude: 0.05, frequency: 2 },
      growth: { duration: 2000, easing: 'easeOutElastic' }
    }
  },

  // Flower - Creative projects, UI/UX, designs
  flower: {
    name: 'Flower',
    description: 'Creative and visual projects, often frontend-focused',
    baseScale: 0.8,
    growthRate: 1.0,
    maxHeight: 1.5,
    categories: ['design', 'frontend', 'creative'],
    characteristics: {
      stem: {
        radius: [0.02, 0.05],
        height: 0.8,
        color: new Color('#4CAF50'),
        material: { roughness: 0.7, metalness: 0.1 }
      },
      petals: {
        radius: 0.3,
        count: 8,
        color: 'project', // Uses project color
        material: { roughness: 0.3, metalness: 0.1 }
      },
      center: {
        radius: 0.1,
        color: new Color('#FFC107'),
        material: { roughness: 0.4, metalness: 0.3 }
      }
    },
    animations: {
      rotate: { speed: 0.5, axis: 'y' },
      pulse: { amplitude: 0.05, frequency: 2 },
      sway: { amplitude: 0.03, frequency: 0.8 }
    }
  },

  // Vine - Collaborative projects, libraries, extensions
  vine: {
    name: 'Vine',
    description: 'Collaborative projects and reusable components',
    baseScale: 0.9,
    growthRate: 0.8,
    maxHeight: 2.0,
    categories: ['library', 'extension', 'tool'],
    characteristics: {
      stem: {
        radius: [0.03, 0.06],
        height: 1.5,
        segments: 12,
        curve: true,
        color: new Color('#2E7D32')
      },
      leaves: {
        count: [3, 7],
        size: 0.2,
        distribution: 'spiral',
        color: 'seasonal'
      },
      tendrils: {
        count: 2,
        length: 0.5,
        animation: 'spiral'
      }
    },
    animations: {
      grow: { direction: 'spiral', speed: 1.5 },
      wave: { amplitude: 0.1, frequency: 0.3 },
      leaf_flutter: { amplitude: 0.02, frequency: 3 }
    }
  },

  // Shrub - Medium projects, utilities, tools
  shrub: {
    name: 'Shrub',
    description: 'Medium-sized utility projects and tools',
    baseScale: 0.7,
    growthRate: 1.1,
    maxHeight: 1.8,
    categories: ['utility', 'tool', 'script'],
    characteristics: {
      base: {
        radius: [0.08, 0.12],
        height: 0.6,
        color: new Color('#795548')
      },
      foliage: {
        count: [2, 4],
        radius: 0.5,
        height: [0.4, 0.8],
        distribution: 'clustered'
      },
      branches: {
        count: [1, 3],
        length: 0.3,
        angle: 45
      }
    },
    animations: {
      rustle: { amplitude: 0.01, frequency: 1.5 },
      grow: { pattern: 'bushy', speed: 1.0 }
    }
  },

  // Grass - Small projects, experiments, prototypes
  grass: {
    name: 'Grass',
    description: 'Small experiments and prototype projects',
    baseScale: 0.3,
    growthRate: 0.5,
    maxHeight: 0.8,
    categories: ['experiment', 'prototype', 'learning'],
    characteristics: {
      blades: {
        count: [3, 8],
        radius: [0.01, 0.02],
        height: [0.2, 0.6],
        color: new Color('#4CAF50'),
        distribution: 'cluster'
      }
    },
    animations: {
      bend: { amplitude: 0.05, frequency: 2 },
      grow: { pattern: 'upward', speed: 0.8 }
    }
  },

  // Mushroom - AI/ML projects, data science
  mushroom: {
    name: 'Mushroom',
    description: 'AI, machine learning, and data science projects',
    baseScale: 0.6,
    growthRate: 0.9,
    maxHeight: 1.2,
    categories: ['ai', 'ml', 'data'],
    characteristics: {
      stem: {
        radius: [0.04, 0.08],
        height: 0.5,
        color: new Color('#FAFAFA')
      },
      cap: {
        radius: 0.4,
        height: 0.2,
        color: 'project',
        spots: true,
        spotColor: new Color('#FFFFFF')
      },
      gills: {
        count: 16,
        visible: true,
        color: new Color('#8D6E63')
      }
    },
    animations: {
      glow: { intensity: 0.3, frequency: 1 },
      expand: { amplitude: 0.02, frequency: 0.5 }
    }
  },

  // Crystal - Blockchain, crypto, cutting-edge tech
  crystal: {
    name: 'Crystal',
    description: 'Blockchain, cryptocurrency, and cutting-edge technology',
    baseScale: 0.8,
    growthRate: 1.3,
    maxHeight: 2.2,
    categories: ['blockchain', 'crypto', 'experimental'],
    characteristics: {
      core: {
        geometry: 'octahedron',
        size: 0.3,
        color: 'project',
        material: { roughness: 0.1, metalness: 0.9 }
      },
      facets: {
        count: 8,
        size: [0.1, 0.2],
        distribution: 'geometric'
      },
      energy: {
        particles: true,
        color: 'project',
        intensity: 0.8
      }
    },
    animations: {
      rotate: { speed: 0.3, axis: 'all' },
      pulse: { intensity: 0.5, frequency: 1.5 },
      energy_flow: { speed: 2, pattern: 'spiral' }
    }
  }
}

export const GROWTH_STAGES = {
  seed: {
    name: 'Seed',
    scale: 0.1,
    opacity: 0.3,
    complexity: 1,
    animationSpeed: 2,
    particleCount: 5,
    glowIntensity: 0.2,
    requirements: { commits: 0, interactions: 0, timeInvested: 0 }
  },
  sprout: {
    name: 'Sprout',
    scale: 0.3,
    opacity: 0.6,
    complexity: 2,
    animationSpeed: 1.5,
    particleCount: 8,
    glowIntensity: 0.4,
    requirements: { commits: 5, interactions: 2, timeInvested: 10 }
  },
  growing: {
    name: 'Growing',
    scale: 0.6,
    opacity: 0.8,
    complexity: 3,
    animationSpeed: 1,
    particleCount: 12,
    glowIntensity: 0.6,
    requirements: { commits: 20, interactions: 10, timeInvested: 40 }
  },
  blooming: {
    name: 'Blooming',
    scale: 0.9,
    opacity: 1,
    complexity: 4,
    animationSpeed: 0.8,
    particleCount: 20,
    glowIntensity: 0.8,
    requirements: { commits: 50, interactions: 30, timeInvested: 100 }
  },
  mature: {
    name: 'Mature',
    scale: 1,
    opacity: 1,
    complexity: 5,
    animationSpeed: 0.5,
    particleCount: 25,
    glowIntensity: 1,
    requirements: { commits: 100, interactions: 60, timeInvested: 200 }
  }
}

// Helper functions
export const getPlantTypeForCategory = (category) => {
  const categoryMap = {
    web: 'tree',
    desktop: 'tree',
    backend: 'tree',
    design: 'flower',
    frontend: 'flower',
    creative: 'flower',
    library: 'vine',
    extension: 'vine',
    tool: 'shrub',
    utility: 'shrub',
    script: 'shrub',
    experiment: 'grass',
    prototype: 'grass',
    learning: 'grass',
    ai: 'mushroom',
    ml: 'mushroom',
    data: 'mushroom',
    blockchain: 'crystal',
    crypto: 'crystal',
    experimental: 'crystal'
  }
  
  return categoryMap[category] || 'flower'
}

export const calculateGrowthStage = (metrics) => {
  const { commits = 0, interactions = 0, timeInvested = 0, complexity = 0 } = metrics
  
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

export const getPlantCharacteristics = (plantType) => {
  return PLANT_TYPES[plantType] || PLANT_TYPES.flower
}

export const getGrowthStageConfig = (stage) => {
  return GROWTH_STAGES[stage] || GROWTH_STAGES.seed
}

export const generatePlantColor = (category, season = 'spring') => {
  const baseColors = {
    web: new Color('#2196F3'),
    desktop: new Color('#9C27B0'),
    backend: new Color('#FF9800'),
    design: new Color('#E91E63'),
    frontend: new Color('#4CAF50'),
    creative: new Color('#FF5722'),
    library: new Color('#795548'),
    extension: new Color('#607D8B'),
    tool: new Color('#3F51B5'),
    utility: new Color('#009688'),
    script: new Color('#FFC107'),
    experiment: new Color('#CDDC39'),
    prototype: new Color('#8BC34A'),
    learning: new Color('#FFEB3B'),
    ai: new Color('#9C27B0'),
    ml: new Color('#673AB7'),
    data: new Color('#3F51B5'),
    blockchain: new Color('#00BCD4'),
    crypto: new Color('#0097A7'),
    experimental: new Color('#006064')
  }
  
  const seasonalModifiers = {
    spring: { h: 0, s: 0.1, l: 0.1 },
    summer: { h: 0.05, s: 0.2, l: 0.15 },
    autumn: { h: 0.1, s: -0.1, l: -0.05 },
    winter: { h: -0.05, s: -0.2, l: -0.1 }
  }
  
  const baseColor = baseColors[category] || new Color('#4CAF50')
  const modifier = seasonalModifiers[season] || seasonalModifiers.spring
  
  const hsl = {}
  baseColor.getHSL(hsl)
  
  return new Color().setHSL(
    Math.max(0, Math.min(1, hsl.h + modifier.h)),
    Math.max(0, Math.min(1, hsl.s + modifier.s)),
    Math.max(0, Math.min(1, hsl.l + modifier.l))
  )
}

export const getPlantAnimations = (plantType, growthStage) => {
  const plantData = PLANT_TYPES[plantType] || PLANT_TYPES.flower
  const stageData = GROWTH_STAGES[growthStage] || GROWTH_STAGES.seed
  
  return {
    ...plantData.animations,
    speedMultiplier: stageData.animationSpeed,
    intensity: stageData.glowIntensity
  }
}

export default PLANT_TYPES