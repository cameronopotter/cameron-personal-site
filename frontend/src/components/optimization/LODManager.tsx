import React, { useMemo, useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { Vector3, Group } from 'three'
import type { ComplexityLevel, LODLevel } from '@/types'

interface LODManagerProps {
  children: React.ReactNode
  complexityLevel: ComplexityLevel
}

interface LODChild {
  element: React.ReactNode
  distance: number
  visible: boolean
}

// LOD configuration based on complexity level
const LODConfigurations: Record<ComplexityLevel, LODLevel[]> = {
  1: [
    { distance: 100, geometry: 'low', material: 'simplified', animations: false, particles: false }
  ],
  2: [
    { distance: 30, geometry: 'low', material: 'simplified', animations: false, particles: false },
    { distance: 100, geometry: 'low', material: 'impostor', animations: false, particles: false }
  ],
  3: [
    { distance: 15, geometry: 'high', material: 'full', animations: true, particles: true },
    { distance: 40, geometry: 'medium', material: 'simplified', animations: true, particles: false },
    { distance: 100, geometry: 'low', material: 'impostor', animations: false, particles: false }
  ],
  4: [
    { distance: 20, geometry: 'high', material: 'full', animations: true, particles: true },
    { distance: 50, geometry: 'medium', material: 'full', animations: true, particles: true },
    { distance: 80, geometry: 'low', material: 'simplified', animations: false, particles: false },
    { distance: 150, geometry: 'low', material: 'impostor', animations: false, particles: false }
  ]
}

export const LODManager: React.FC<LODManagerProps> = ({ 
  children, 
  complexityLevel 
}) => {
  const groupRef = useRef<Group>(null!)
  const { camera } = useThree()
  const lodConfig = LODConfigurations[complexityLevel]
  
  // Track visible children based on distance
  const visibleChildren = useMemo(() => {
    return React.Children.map(children, (child, index) => {
      return {
        element: child,
        distance: 0,
        visible: true,
        index
      }
    }) as LODChild[]
  }, [children])

  useFrame(() => {
    if (!groupRef.current) return

    const cameraPosition = camera.position
    
    // Update visibility based on distance for each child
    React.Children.forEach(children, (child, index) => {
      if (React.isValidElement(child) && child.props.position) {
        const childPosition = new Vector3(...child.props.position)
        const distance = cameraPosition.distanceTo(childPosition)
        
        // Find appropriate LOD level
        const lodLevel = lodConfig.find(config => distance <= config.distance) || lodConfig[lodConfig.length - 1]
        
        // Update child visibility and detail level
        if (visibleChildren[index]) {
          visibleChildren[index].distance = distance
          visibleChildren[index].visible = distance <= lodConfig[lodConfig.length - 1].distance
          
          // Pass LOD information to child components
          if (typeof child.props.onLODUpdate === 'function') {
            child.props.onLODUpdate(lodLevel)
          }
        }
      }
    })
  })

  return (
    <group ref={groupRef}>
      {React.Children.map(children, (child, index) => {
        if (!React.isValidElement(child)) return child
        
        const lodChild = visibleChildren[index]
        if (!lodChild?.visible) return null

        // Clone child with LOD properties
        return React.cloneElement(child as React.ReactElement<any>, {
          ...child.props,
          lodDistance: lodChild.distance,
          complexityLevel
        })
      })}
    </group>
  )
}