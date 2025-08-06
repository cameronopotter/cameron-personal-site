import React, { useRef, useMemo, useState, useCallback } from 'react'
import { useFrame, useLoader } from '@react-three/fiber'
import { Text, useGLTF, Float, Trail, Sparkles } from '@react-three/drei'
import { 
  Mesh, 
  Group, 
  Vector3, 
  Color, 
  MathUtils, 
  CylinderGeometry, 
  SphereGeometry,
  ConeGeometry,
  MeshStandardMaterial,
  DoubleSide,
  BackSide
} from 'three'
import { useSpring, animated } from '@react-spring/three'
import { motion } from 'framer-motion'
import type { ProjectPlantProps, GrowthStage, InteractionType, Project } from '@/types'

// Plant geometries for different project types
const PlantGeometry = {
  tree: {
    trunk: new CylinderGeometry(0.1, 0.15, 1, 8),
    canopy: new SphereGeometry(0.8, 16, 12),
    leaves: new ConeGeometry(0.6, 1.2, 8)
  },
  flower: {
    stem: new CylinderGeometry(0.02, 0.05, 0.8, 6),
    petals: new SphereGeometry(0.3, 12, 8),
    center: new SphereGeometry(0.1, 8, 6)
  },
  vine: {
    stem: new CylinderGeometry(0.03, 0.06, 1.5, 8),
    leaves: new SphereGeometry(0.2, 8, 6)
  },
  shrub: {
    base: new CylinderGeometry(0.08, 0.12, 0.6, 8),
    foliage: new SphereGeometry(0.5, 12, 8)
  },
  grass: {
    blade: new CylinderGeometry(0.01, 0.02, 0.4, 4)
  }
}

// Growth stage configurations
const GrowthConfigurations: Record<GrowthStage, {
  scale: number
  opacity: number
  complexity: number
  animationSpeed: number
  particleCount: number
  glowIntensity: number
}> = {
  seed: { 
    scale: 0.1, 
    opacity: 0.3, 
    complexity: 1, 
    animationSpeed: 2, 
    particleCount: 5, 
    glowIntensity: 0.2 
  },
  sprout: { 
    scale: 0.3, 
    opacity: 0.6, 
    complexity: 2, 
    animationSpeed: 1.5, 
    particleCount: 8, 
    glowIntensity: 0.4 
  },
  growing: { 
    scale: 0.6, 
    opacity: 0.8, 
    complexity: 3, 
    animationSpeed: 1, 
    particleCount: 12, 
    glowIntensity: 0.6 
  },
  blooming: { 
    scale: 0.9, 
    opacity: 1, 
    complexity: 4, 
    animationSpeed: 0.8, 
    particleCount: 20, 
    glowIntensity: 0.8 
  },
  mature: { 
    scale: 1, 
    opacity: 1, 
    complexity: 5, 
    animationSpeed: 0.5, 
    particleCount: 25, 
    glowIntensity: 1 
  }
}

// Individual Plant Components
const TreePlant: React.FC<{ 
  project: Project, 
  config: typeof GrowthConfigurations.mature,
  isHovered: boolean,
  isSelected: boolean 
}> = ({ project, config, isHovered, isSelected }) => {
  const trunkRef = useRef<Mesh>(null!)
  const canopyRef = useRef<Mesh>(null!)
  
  const { scale, opacity, complexity } = config
  
  // Materials based on project category and growth
  const trunkMaterial = useMemo(() => new MeshStandardMaterial({
    color: new Color('#8D6E63'),
    roughness: 0.8,
    metalness: 0.1
  }), [])
  
  const canopyMaterial = useMemo(() => new MeshStandardMaterial({
    color: project.color,
    roughness: 0.6,
    metalness: 0.2,
    transparent: true,
    opacity: opacity * (isHovered ? 1.2 : 1)
  }), [project.color, opacity, isHovered])
  
  // Gentle swaying animation
  useFrame((state) => {
    if (trunkRef.current && canopyRef.current) {
      const time = state.clock.getElapsedTime() * config.animationSpeed
      const sway = Math.sin(time) * 0.02
      
      trunkRef.current.rotation.z = sway
      canopyRef.current.rotation.z = sway * 1.2
      canopyRef.current.position.y = 1 + Math.sin(time * 2) * 0.05
    }
  })
  
  return (
    <group scale={scale}>
      {/* Trunk */}
      <mesh
        ref={trunkRef}
        geometry={PlantGeometry.tree.trunk}
        material={trunkMaterial}
        position={[0, 0.5, 0]}
        castShadow
        receiveShadow
      />
      
      {/* Canopy */}
      <mesh
        ref={canopyRef}
        geometry={PlantGeometry.tree.canopy}
        material={canopyMaterial}
        position={[0, 1.2, 0]}
        castShadow
        receiveShadow
      />
      
      {/* Additional leaves for complexity */}
      {complexity > 3 && Array.from({ length: 3 }).map((_, i) => (
        <mesh
          key={`leaf-${i}`}
          geometry={PlantGeometry.tree.leaves}
          material={canopyMaterial}
          position={[
            Math.cos((i * Math.PI * 2) / 3) * 0.6,
            1.5,
            Math.sin((i * Math.PI * 2) / 3) * 0.6
          ]}
          scale={0.3}
          rotation={[0, (i * Math.PI * 2) / 3, 0]}
        />
      ))}
    </group>
  )
}

const FlowerPlant: React.FC<{ 
  project: Project, 
  config: typeof GrowthConfigurations.mature,
  isHovered: boolean,
  isSelected: boolean 
}> = ({ project, config, isHovered, isSelected }) => {
  const stemRef = useRef<Mesh>(null!)
  const petalsRef = useRef<Mesh>(null!)
  
  const { scale, opacity } = config
  
  const stemMaterial = useMemo(() => new MeshStandardMaterial({
    color: new Color('#4CAF50'),
    roughness: 0.7,
    metalness: 0.1
  }), [])
  
  const petalsMaterial = useMemo(() => new MeshStandardMaterial({
    color: project.color,
    roughness: 0.3,
    metalness: 0.1,
    transparent: true,
    opacity: opacity,
    emissive: isSelected ? project.color.clone().multiplyScalar(0.3) : new Color(0x000000)
  }), [project.color, opacity, isSelected])
  
  const centerMaterial = useMemo(() => new MeshStandardMaterial({
    color: new Color('#FFC107'),
    roughness: 0.4,
    metalness: 0.3
  }), [])
  
  // Petal movement animation
  useFrame((state) => {
    if (petalsRef.current) {
      const time = state.clock.getElapsedTime() * config.animationSpeed
      petalsRef.current.rotation.y = time * 0.5
      petalsRef.current.scale.setScalar(1 + Math.sin(time * 2) * 0.05)
    }
    
    if (stemRef.current) {
      const sway = Math.sin(state.clock.getElapsedTime()) * 0.03
      stemRef.current.rotation.z = sway
    }
  })
  
  return (
    <group scale={scale}>
      {/* Stem */}
      <mesh
        ref={stemRef}
        geometry={PlantGeometry.flower.stem}
        material={stemMaterial}
        position={[0, 0.4, 0]}
        castShadow
      />
      
      {/* Petals */}
      <mesh
        ref={petalsRef}
        geometry={PlantGeometry.flower.petals}
        material={petalsMaterial}
        position={[0, 0.9, 0]}
        castShadow
      />
      
      {/* Center */}
      <mesh
        geometry={PlantGeometry.flower.center}
        material={centerMaterial}
        position={[0, 0.9, 0]}
        castShadow
      />
    </group>
  )
}

// Main ProjectPlant Component
export const ProjectPlant: React.FC<ProjectPlantProps> = ({
  project,
  isSelected = false,
  onInteract,
  level
}) => {
  const groupRef = useRef<Group>(null!)
  const [isHovered, setIsHovered] = useState(false)
  const [isClicked, setIsClicked] = useState(false)
  
  // Get growth configuration
  const growthConfig = GrowthConfigurations[project.growthStage]
  
  // Spring animations for interactions
  const { scale, position, rotation } = useSpring({
    scale: isHovered ? growthConfig.scale * 1.1 : growthConfig.scale,
    position: project.position,
    rotation: isSelected ? [0, Math.PI * 2, 0] : [0, 0, 0],
    config: { tension: 300, friction: 30 }
  })
  
  // Glow effect for selected/hovered states
  const glowIntensity = useMemo(() => {
    let intensity = growthConfig.glowIntensity
    if (isSelected) intensity *= 1.5
    if (isHovered) intensity *= 1.2
    return intensity
  }, [growthConfig.glowIntensity, isSelected, isHovered])
  
  // Interaction handlers
  const handlePointerOver = useCallback((event: any) => {
    event.stopPropagation()
    setIsHovered(true)
    onInteract?.('hover')
    document.body.style.cursor = 'pointer'
  }, [onInteract])
  
  const handlePointerOut = useCallback((event: any) => {
    event.stopPropagation()
    setIsHovered(false)
    document.body.style.cursor = 'default'
  }, [])
  
  const handleClick = useCallback((event: any) => {
    event.stopPropagation()
    setIsClicked(true)
    onInteract?.('click')
    setTimeout(() => setIsClicked(false), 200)
  }, [onInteract])
  
  const handleLongPress = useCallback((event: any) => {
    event.stopPropagation()
    onInteract?.('longPress')
  }, [onInteract])
  
  // Floating animation
  const floatAmplitude = growthConfig.scale * 0.05
  const floatSpeed = 2 - growthConfig.animationSpeed
  
  // Performance optimization: reduce complexity based on level
  const shouldShowParticles = level > 2 && (isHovered || isSelected)
  const shouldShowText = level > 1 && (isHovered || isSelected)
  const shouldShowTrail = level > 3 && isSelected
  
  // Plant component selection
  const PlantComponent = useMemo(() => {
    switch (project.plantType) {
      case 'tree':
        return TreePlant
      case 'flower':
        return FlowerPlant
      case 'vine':
        return FlowerPlant // Simplified for now
      case 'shrub':
        return TreePlant // Simplified for now
      case 'grass':
        return FlowerPlant // Simplified for now
      default:
        return TreePlant
    }
  }, [project.plantType])
  
  return (
    <animated.group
      ref={groupRef}
      position={position as any}
      scale={scale as any}
      rotation={rotation as any}
      onPointerOver={handlePointerOver}
      onPointerOut={handlePointerOut}
      onClick={handleClick}
      onPointerDown={handleLongPress}
    >
      {/* Main Plant with Float animation */}
      <Float
        speed={floatSpeed}
        rotationIntensity={0.1}
        floatIntensity={floatAmplitude}
        floatingRange={[0, floatAmplitude * 2]}
      >
        {/* Sparkle effects for active projects */}
        {shouldShowParticles && (
          <Sparkles
            count={growthConfig.particleCount}
            scale={[2, 2, 2]}
            size={3}
            speed={0.6}
            opacity={0.6}
            color={project.color}
          />
        )}
        
        {/* Trail effect for selected projects */}
        {shouldShowTrail && (
          <Trail
            width={0.5}
            length={8}
            color={project.color}
            attenuation={(t) => t * t}
          >
            <PlantComponent
              project={project}
              config={growthConfig}
              isHovered={isHovered}
              isSelected={isSelected}
            />
          </Trail>
        )}
        
        {!shouldShowTrail && (
          <PlantComponent
            project={project}
            config={growthConfig}
            isHovered={isHovered}
            isSelected={isSelected}
          />
        )}
        
        {/* Project Label */}
        {shouldShowText && (
          <Text
            position={[0, 2.5, 0]}
            fontSize={0.3}
            color={project.color}
            anchorX="center"
            anchorY="middle"
            font="/fonts/Inter-Medium.woff"
            maxWidth={3}
            textAlign="center"
          >
            {project.name}
            {level > 2 && (
              <meshStandardMaterial 
                color={project.color}
                emissive={project.color.clone().multiplyScalar(0.2)}
                transparent
                opacity={0.9}
              />
            )}
          </Text>
        )}
        
        {/* Growth stage indicator */}
        {level > 2 && isHovered && (
          <Text
            position={[0, -0.5, 0]}
            fontSize={0.15}
            color="#ffffff"
            anchorX="center"
            anchorY="middle"
            font="/fonts/Inter-Regular.woff"
            maxWidth={2}
            textAlign="center"
          >
            {project.growthStage.toUpperCase()}
            <meshStandardMaterial 
              color="#ffffff"
              transparent
              opacity={0.7}
            />
          </Text>
        )}
        
        {/* Glow Effect */}
        {glowIntensity > 0.5 && level > 2 && (
          <mesh position={[0, 1, 0]}>
            <sphereGeometry args={[2, 16, 12]} />
            <meshBasicMaterial
              color={project.color}
              transparent
              opacity={glowIntensity * 0.1}
              side={BackSide}
            />
          </mesh>
        )}
        
        {/* Click Effect */}
        {isClicked && level > 1 && (
          <mesh position={[0, 1, 0]}>
            <ringGeometry args={[1, 1.5, 16]} />
            <meshBasicMaterial
              color={project.color}
              transparent
              opacity={0.8}
              side={DoubleSide}
            />
          </mesh>
        )}
      </Float>
      
      {/* Project Stats (visible on hover for high complexity) */}
      {level > 3 && isHovered && (
        <group position={[0, 3, 0]}>
          <Text
            position={[0, 0.3, 0]}
            fontSize={0.12}
            color="#8BC34A"
            anchorX="center"
            font="/fonts/Inter-Regular.woff"
          >
            Commits: {project.growthMetrics.commits}
          </Text>
          <Text
            position={[0, 0.1, 0]}
            fontSize={0.12}
            color="#2196F3"
            anchorX="center"
            font="/fonts/Inter-Regular.woff"
          >
            Interactions: {project.growthMetrics.interactions}
          </Text>
          <Text
            position={[0, -0.1, 0]}
            fontSize={0.12}
            color="#FF9800"
            anchorX="center"
            font="/fonts/Inter-Regular.woff"
          >
            Hours: {Math.round(project.growthMetrics.timeInvested)}
          </Text>
        </group>
      )}
    </animated.group>
  )
}