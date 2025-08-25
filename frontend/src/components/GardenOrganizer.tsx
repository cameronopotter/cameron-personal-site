import React, { useMemo } from 'react'
import { Vector3 } from 'three'

interface GardenOrganizerProps {
  projects: Array<{
    id: string
    name: string
    position: [number, number, number]
    importance: number
    plantType: string
  }>
}

// Smart garden layout system for optimal organization
export const useGardenLayout = (projects: GardenOrganizerProps['projects']) => {
  return useMemo(() => {
    if (projects.length === 0) return []

    // Sort projects by importance for optimal placement
    const sortedProjects = [...projects].sort((a, b) => b.importance - a.importance)
    
    // Create organized sections for different types of content
    const sections = {
      // Central area for most important projects (radius 0-8)
      central: { center: [0, 0, 0], radius: 8, positions: [] as Array<[number, number, number]> },
      
      // Mid ring for moderately important projects (radius 8-15)
      midRing: { center: [0, 0, 0], radius: 12, minRadius: 8, positions: [] as Array<[number, number, number]> },
      
      // Outer ring for supporting projects (radius 15-22)
      outerRing: { center: [0, 0, 0], radius: 20, minRadius: 15, positions: [] as Array<[number, number, number]> },
    }
    
    // Position calculation with spiral and clustered layouts
    const getOptimalPosition = (index: number, total: number, section: typeof sections.central): [number, number, number] => {
      if (section.radius <= 8) {
        // Central area: tight spiral for important projects
        const angle = index * (Math.PI * 2 / Math.max(total, 1)) + Math.random() * 0.5
        const radius = Math.random() * section.radius
        return [
          Math.cos(angle) * radius,
          0,
          Math.sin(angle) * radius
        ]
      } else {
        // Ring areas: distributed around the perimeter
        const angle = index * (Math.PI * 2 / Math.max(total, 1)) + Math.random() * 0.8
        const radius = (section.minRadius || 0) + Math.random() * (section.radius - (section.minRadius || 0))
        return [
          Math.cos(angle) * radius,
          0,
          Math.sin(angle) * radius
        ]
      }
    }
    
    // Distribute projects across sections based on importance
    const centralCount = Math.min(5, Math.ceil(sortedProjects.length * 0.3))
    const midRingCount = Math.min(8, Math.ceil(sortedProjects.length * 0.4))
    const outerRingCount = sortedProjects.length - centralCount - midRingCount
    
    const organizedProjects = sortedProjects.map((project, index) => {
      let position: [number, number, number]
      let section: 'central' | 'midRing' | 'outerRing'
      
      if (index < centralCount) {
        position = getOptimalPosition(index, centralCount, sections.central)
        section = 'central'
      } else if (index < centralCount + midRingCount) {
        position = getOptimalPosition(index - centralCount, midRingCount, sections.midRing)
        section = 'midRing'
      } else {
        position = getOptimalPosition(index - centralCount - midRingCount, outerRingCount, sections.outerRing)
        section = 'outerRing'
      }
      
      return {
        ...project,
        position,
        section,
        // Enhanced positioning with slight height variation for visual interest
        finalPosition: [
          position[0],
          Math.random() * 0.2, // Slight height variation
          position[2]
        ] as [number, number, number]
      }
    })
    
    return organizedProjects
  }, [projects])
}

// Path generation for neon roads connecting important areas
export const usePathNetwork = (organizedProjects: ReturnType<typeof useGardenLayout>) => {
  return useMemo(() => {
    const paths = []
    
    // Main arterial paths from center to outer sections
    const centralProjects = organizedProjects.filter(p => p.section === 'central')
    const midRingProjects = organizedProjects.filter(p => p.section === 'midRing')
    const outerRingProjects = organizedProjects.filter(p => p.section === 'outerRing')
    
    // Connect center to major outer projects
    centralProjects.slice(0, 3).forEach((central, index) => {
      const targets = [...midRingProjects.slice(0, 2), ...outerRingProjects.slice(0, 1)]
      targets.forEach((target, targetIndex) => {
        if (targetIndex % 2 === index % 2) { // Connect selectively to avoid overcrowding
          paths.push({
            id: `path-central-${index}-${targetIndex}`,
            start: central.finalPosition,
            end: target.finalPosition,
            type: 'main',
            color: '#00FFFF'
          })
        }
      })
    })
    
    // Circular paths connecting sections
    const createCircularPath = (projects: typeof organizedProjects, pathType: string, color: string) => {
      projects.forEach((project, index) => {
        const nextProject = projects[(index + 1) % projects.length]
        paths.push({
          id: `${pathType}-${index}`,
          start: project.finalPosition,
          end: nextProject.finalPosition,
          type: pathType,
          color
        })
      })
    }
    
    if (midRingProjects.length > 2) {
      createCircularPath(midRingProjects, 'midRing', '#FF1493')
    }
    
    if (outerRingProjects.length > 2) {
      createCircularPath(outerRingProjects, 'outerRing', '#00FF00')
    }
    
    return paths
  }, [organizedProjects])
}

// Lighting zones for different areas of the garden
export const useLightingZones = (organizedProjects: ReturnType<typeof useGardenLayout>) => {
  return useMemo(() => {
    const zones = []
    
    // Central spotlight for most important projects
    const centralProjects = organizedProjects.filter(p => p.section === 'central')
    if (centralProjects.length > 0) {
      const centerPoint = centralProjects.reduce(
        (avg, project) => [
          avg[0] + project.finalPosition[0] / centralProjects.length,
          avg[1] + project.finalPosition[1] / centralProjects.length,
          avg[2] + project.finalPosition[2] / centralProjects.length
        ],
        [0, 0, 0] as [number, number, number]
      )
      
      zones.push({
        id: 'central-spotlight',
        position: [centerPoint[0], 8, centerPoint[2]],
        color: '#FFFFFF',
        intensity: 3,
        distance: 20,
        type: 'spotlight'
      })
    }
    
    // Ambient colored lights for sections
    const sectionColors = {
      central: '#00FFFF',
      midRing: '#FF1493', 
      outerRing: '#00FF00'
    }
    
    Object.entries(sectionColors).forEach(([sectionName, color]) => {
      const sectionProjects = organizedProjects.filter(p => p.section === sectionName)
      sectionProjects.forEach((project, index) => {
        zones.push({
          id: `${sectionName}-light-${index}`,
          position: [
            project.finalPosition[0],
            4 + Math.random() * 2,
            project.finalPosition[2]
          ],
          color,
          intensity: 1.5,
          distance: 12,
          type: 'ambient'
        })
      })
    })
    
    return zones
  }, [organizedProjects])
}