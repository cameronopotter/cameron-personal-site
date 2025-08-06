import React, { useRef, useMemo, useCallback } from 'react'
import { useFrame } from '@react-three/fiber'
import { Points, PointMaterial } from '@react-three/drei'
import { 
  Vector3, 
  Color, 
  BufferGeometry, 
  Float32BufferAttribute, 
  Points as ThreePoints,
  AdditiveBlending,
  NormalBlending
} from 'three'
import { createNoise3D } from 'simplex-noise'
import type { WeatherSystemProps, WeatherMood } from '@/types'

// Particle system configurations for different weather types
const WeatherConfigs = {
  rain: {
    count: 2000,
    spread: 50,
    speed: [8, 12],
    size: [0.05, 0.1],
    life: [2, 4],
    gravity: 9.8,
    opacity: [0.3, 0.7],
    color: new Color('#87CEEB'),
    blending: NormalBlending,
    shape: 'line'
  },
  snow: {
    count: 1500,
    spread: 60,
    speed: [1, 3],
    size: [0.1, 0.3],
    life: [5, 8],
    gravity: 2,
    opacity: [0.4, 0.8],
    color: new Color('#FFFFFF'),
    blending: AdditiveBlending,
    shape: 'dot'
  },
  sparkles: {
    count: 800,
    spread: 40,
    speed: [0.5, 2],
    size: [0.05, 0.2],
    life: [3, 6],
    gravity: -1,
    opacity: [0.5, 1.0],
    color: new Color('#FFD700'),
    blending: AdditiveBlending,
    shape: 'star'
  },
  leaves: {
    count: 1200,
    spread: 45,
    speed: [2, 5],
    size: [0.1, 0.25],
    life: [4, 7],
    gravity: 3,
    opacity: [0.6, 0.9],
    color: new Color('#FF5722'),
    blending: NormalBlending,
    shape: 'leaf'
  },
  aurora: {
    count: 500,
    spread: 80,
    speed: [0.2, 1],
    size: [0.2, 0.5],
    life: [8, 12],
    gravity: 0,
    opacity: [0.2, 0.6],
    color: new Color('#00FF88'),
    blending: AdditiveBlending,
    shape: 'wave'
  }
}

// Individual particle system components
const RainParticles: React.FC<{ config: typeof WeatherConfigs.rain; intensity: number }> = ({ 
  config, 
  intensity 
}) => {
  const pointsRef = useRef<ThreePoints>(null!)
  const particleCount = Math.floor(config.count * intensity)
  
  // Initialize particle positions and velocities
  const { positions, velocities, sizes, opacities } = useMemo(() => {
    const positions = new Float32Array(particleCount * 3)
    const velocities = new Float32Array(particleCount * 3)
    const sizes = new Float32Array(particleCount)
    const opacities = new Float32Array(particleCount)
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3
      
      // Random positions within spread area
      positions[i3] = (Math.random() - 0.5) * config.spread
      positions[i3 + 1] = Math.random() * 30 + 10 // Start high
      positions[i3 + 2] = (Math.random() - 0.5) * config.spread
      
      // Downward velocity with slight randomness
      velocities[i3] = (Math.random() - 0.5) * 2
      velocities[i3 + 1] = -Math.random() * (config.speed[1] - config.speed[0]) - config.speed[0]
      velocities[i3 + 2] = (Math.random() - 0.5) * 2
      
      sizes[i] = Math.random() * (config.size[1] - config.size[0]) + config.size[0]
      opacities[i] = Math.random() * (config.opacity[1] - config.opacity[0]) + config.opacity[0]
    }
    
    return { positions, velocities, sizes, opacities }
  }, [particleCount, config])
  
  // Animate particles
  useFrame((state, delta) => {
    if (!pointsRef.current) return
    
    const positions = pointsRef.current.geometry.attributes.position.array as Float32Array
    const opacityArray = pointsRef.current.geometry.attributes.opacity.array as Float32Array
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3
      
      // Update positions based on velocities
      positions[i3] += velocities[i3] * delta
      positions[i3 + 1] += velocities[i3 + 1] * delta
      positions[i3 + 2] += velocities[i3 + 2] * delta
      
      // Apply gravity
      velocities[i3 + 1] -= config.gravity * delta
      
      // Reset particles that fall below ground
      if (positions[i3 + 1] < -1) {
        positions[i3] = (Math.random() - 0.5) * config.spread
        positions[i3 + 1] = 30
        positions[i3 + 2] = (Math.random() - 0.5) * config.spread
        velocities[i3 + 1] = -Math.random() * (config.speed[1] - config.speed[0]) - config.speed[0]
      }
      
      // Fade out particles near ground
      const heightFactor = Math.max(0, Math.min(1, (positions[i3 + 1] + 1) / 2))
      opacityArray[i] = opacities[i] * heightFactor * intensity
    }
    
    pointsRef.current.geometry.attributes.position.needsUpdate = true
    pointsRef.current.geometry.attributes.opacity.needsUpdate = true
  })
  
  const geometry = useMemo(() => {
    const geo = new BufferGeometry()
    geo.setAttribute('position', new Float32BufferAttribute(positions, 3))
    geo.setAttribute('opacity', new Float32BufferAttribute(opacities, 1))
    geo.setAttribute('size', new Float32BufferAttribute(sizes, 1))
    return geo
  }, [positions, opacities, sizes])
  
  return (
    <points ref={pointsRef} geometry={geometry}>
      <pointsMaterial
        size={0.1}
        color={config.color}
        transparent
        opacity={intensity}
        blending={config.blending}
        sizeAttenuation
        vertexColors={false}
      />
    </points>
  )
}

const SnowParticles: React.FC<{ config: typeof WeatherConfigs.snow; intensity: number }> = ({ 
  config, 
  intensity 
}) => {
  const pointsRef = useRef<ThreePoints>(null!)
  const particleCount = Math.floor(config.count * intensity)
  const noise3D = useMemo(() => createNoise3D(), [])
  
  const { positions, velocities, sizes, life } = useMemo(() => {
    const positions = new Float32Array(particleCount * 3)
    const velocities = new Float32Array(particleCount * 3)
    const sizes = new Float32Array(particleCount)
    const life = new Float32Array(particleCount)
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3
      
      positions[i3] = (Math.random() - 0.5) * config.spread
      positions[i3 + 1] = Math.random() * 25 + 5
      positions[i3 + 2] = (Math.random() - 0.5) * config.spread
      
      velocities[i3] = (Math.random() - 0.5) * 1
      velocities[i3 + 1] = -Math.random() * (config.speed[1] - config.speed[0]) - config.speed[0]
      velocities[i3 + 2] = (Math.random() - 0.5) * 1
      
      sizes[i] = Math.random() * (config.size[1] - config.size[0]) + config.size[0]
      life[i] = Math.random() * (config.life[1] - config.life[0]) + config.life[0]
    }
    
    return { positions, velocities, sizes, life }
  }, [particleCount, config])
  
  useFrame((state, delta) => {
    if (!pointsRef.current) return
    
    const positions = pointsRef.current.geometry.attributes.position.array as Float32Array
    const time = state.clock.getElapsedTime()
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3
      
      // Add noise for realistic drift
      const noiseX = noise3D(positions[i3] * 0.01, positions[i3 + 2] * 0.01, time * 0.5) * 2
      const noiseZ = noise3D(positions[i3 + 2] * 0.01, positions[i3] * 0.01, time * 0.3) * 2
      
      positions[i3] += (velocities[i3] + noiseX) * delta
      positions[i3 + 1] += velocities[i3 + 1] * delta
      positions[i3 + 2] += (velocities[i3 + 2] + noiseZ) * delta
      
      // Reset particles that fall below ground or drift too far
      if (positions[i3 + 1] < -1 || Math.abs(positions[i3]) > config.spread || Math.abs(positions[i3 + 2]) > config.spread) {
        positions[i3] = (Math.random() - 0.5) * config.spread
        positions[i3 + 1] = 25
        positions[i3 + 2] = (Math.random() - 0.5) * config.spread
      }
    }
    
    pointsRef.current.geometry.attributes.position.needsUpdate = true
  })
  
  const geometry = useMemo(() => {
    const geo = new BufferGeometry()
    geo.setAttribute('position', new Float32BufferAttribute(positions, 3))
    geo.setAttribute('size', new Float32BufferAttribute(sizes, 1))
    return geo
  }, [positions, sizes])
  
  return (
    <points ref={pointsRef} geometry={geometry}>
      <pointsMaterial
        size={0.2}
        color={config.color}
        transparent
        opacity={intensity}
        blending={config.blending}
        sizeAttenuation
      />
    </points>
  )
}

const SparkleParticles: React.FC<{ config: typeof WeatherConfigs.sparkles; intensity: number }> = ({ 
  config, 
  intensity 
}) => {
  const pointsRef = useRef<ThreePoints>(null!)
  const particleCount = Math.floor(config.count * intensity)
  
  const { positions, velocities, colors, sizes } = useMemo(() => {
    const positions = new Float32Array(particleCount * 3)
    const velocities = new Float32Array(particleCount * 3)
    const colors = new Float32Array(particleCount * 3)
    const sizes = new Float32Array(particleCount)
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3
      
      positions[i3] = (Math.random() - 0.5) * config.spread
      positions[i3 + 1] = Math.random() * 15 + 2
      positions[i3 + 2] = (Math.random() - 0.5) * config.spread
      
      // Sparkles float gently upward
      velocities[i3] = (Math.random() - 0.5) * 0.5
      velocities[i3 + 1] = Math.random() * (config.speed[1] - config.speed[0]) + config.speed[0]
      velocities[i3 + 2] = (Math.random() - 0.5) * 0.5
      
      // Randomize colors slightly
      const hue = Math.random() * 0.1 + 0.15 // Yellow-gold range
      const saturation = 0.8 + Math.random() * 0.2
      const lightness = 0.5 + Math.random() * 0.5
      
      const color = new Color().setHSL(hue, saturation, lightness)
      colors[i3] = color.r
      colors[i3 + 1] = color.g
      colors[i3 + 2] = color.b
      
      sizes[i] = Math.random() * (config.size[1] - config.size[0]) + config.size[0]
    }
    
    return { positions, velocities, colors, sizes }
  }, [particleCount, config])
  
  useFrame((state, delta) => {
    if (!pointsRef.current) return
    
    const positions = pointsRef.current.geometry.attributes.position.array as Float32Array
    const time = state.clock.getElapsedTime()
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3
      
      // Gentle floating motion
      positions[i3] += velocities[i3] * delta + Math.sin(time + i) * 0.01
      positions[i3 + 1] += velocities[i3 + 1] * delta
      positions[i3 + 2] += velocities[i3 + 2] * delta + Math.cos(time + i) * 0.01
      
      // Reset particles that float too high
      if (positions[i3 + 1] > 20) {
        positions[i3] = (Math.random() - 0.5) * config.spread
        positions[i3 + 1] = 0
        positions[i3 + 2] = (Math.random() - 0.5) * config.spread
      }
    }
    
    pointsRef.current.geometry.attributes.position.needsUpdate = true
  })
  
  const geometry = useMemo(() => {
    const geo = new BufferGeometry()
    geo.setAttribute('position', new Float32BufferAttribute(positions, 3))
    geo.setAttribute('color', new Float32BufferAttribute(colors, 3))
    geo.setAttribute('size', new Float32BufferAttribute(sizes, 1))
    return geo
  }, [positions, colors, sizes])
  
  return (
    <points ref={pointsRef} geometry={geometry}>
      <pointsMaterial
        size={0.15}
        transparent
        opacity={intensity * 0.8}
        blending={config.blending}
        sizeAttenuation
        vertexColors
      />
    </points>
  )
}

const LeafParticles: React.FC<{ config: typeof WeatherConfigs.leaves; intensity: number }> = ({ 
  config, 
  intensity 
}) => {
  const pointsRef = useRef<ThreePoints>(null!)
  const particleCount = Math.floor(config.count * intensity)
  const noise3D = useMemo(() => createNoise3D(), [])
  
  const { positions, velocities, rotations, colors } = useMemo(() => {
    const positions = new Float32Array(particleCount * 3)
    const velocities = new Float32Array(particleCount * 3)
    const rotations = new Float32Array(particleCount)
    const colors = new Float32Array(particleCount * 3)
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3
      
      positions[i3] = (Math.random() - 0.5) * config.spread
      positions[i3 + 1] = Math.random() * 20 + 10
      positions[i3 + 2] = (Math.random() - 0.5) * config.spread
      
      velocities[i3] = (Math.random() - 0.5) * 3
      velocities[i3 + 1] = -Math.random() * (config.speed[1] - config.speed[0]) - config.speed[0]
      velocities[i3 + 2] = (Math.random() - 0.5) * 3
      
      rotations[i] = Math.random() * Math.PI * 2
      
      // Autumn leaf colors
      const leafColors = [
        new Color('#FF5722'), // Orange
        new Color('#FFC107'), // Yellow
        new Color('#8D6E63'), // Brown
        new Color('#F44336'), // Red
        new Color('#FF8F00'), // Amber
      ]
      const color = leafColors[Math.floor(Math.random() * leafColors.length)]
      colors[i3] = color.r
      colors[i3 + 1] = color.g
      colors[i3 + 2] = color.b
    }
    
    return { positions, velocities, rotations, colors }
  }, [particleCount, config])
  
  useFrame((state, delta) => {
    if (!pointsRef.current) return
    
    const positions = pointsRef.current.geometry.attributes.position.array as Float32Array
    const time = state.clock.getElapsedTime()
    
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3
      
      // Swirling motion with noise
      const noiseX = noise3D(positions[i3] * 0.02, positions[i3 + 1] * 0.02, time * 0.1) * 3
      const noiseZ = noise3D(positions[i3 + 2] * 0.02, positions[i3] * 0.02, time * 0.15) * 3
      
      positions[i3] += (velocities[i3] + noiseX) * delta
      positions[i3 + 1] += velocities[i3 + 1] * delta
      positions[i3 + 2] += (velocities[i3 + 2] + noiseZ) * delta
      
      // Apply gravity with air resistance
      velocities[i3 + 1] -= config.gravity * delta * 0.5
      velocities[i3] *= 0.99 // Air resistance
      velocities[i3 + 2] *= 0.99
      
      // Reset leaves that fall below ground
      if (positions[i3 + 1] < -1) {
        positions[i3] = (Math.random() - 0.5) * config.spread
        positions[i3 + 1] = 20
        positions[i3 + 2] = (Math.random() - 0.5) * config.spread
        velocities[i3] = (Math.random() - 0.5) * 3
        velocities[i3 + 1] = -Math.random() * (config.speed[1] - config.speed[0]) - config.speed[0]
        velocities[i3 + 2] = (Math.random() - 0.5) * 3
      }
    }
    
    pointsRef.current.geometry.attributes.position.needsUpdate = true
  })
  
  const geometry = useMemo(() => {
    const geo = new BufferGeometry()
    geo.setAttribute('position', new Float32BufferAttribute(positions, 3))
    geo.setAttribute('color', new Float32BufferAttribute(colors, 3))
    return geo
  }, [positions, colors])
  
  return (
    <points ref={pointsRef} geometry={geometry}>
      <pointsMaterial
        size={0.2}
        transparent
        opacity={intensity}
        blending={config.blending}
        sizeAttenuation
        vertexColors
      />
    </points>
  )
}

// Main WeatherSystem Component
export const WeatherSystem: React.FC<WeatherSystemProps> = ({
  weather,
  enabled,
  intensity = 1
}) => {
  const config = WeatherConfigs[weather.particles.type]
  const effectiveIntensity = intensity * weather.intensity
  
  if (!enabled || effectiveIntensity <= 0) {
    return null
  }
  
  const renderParticleSystem = useCallback(() => {
    switch (weather.particles.type) {
      case 'rain':
        return <RainParticles config={config as typeof WeatherConfigs.rain} intensity={effectiveIntensity} />
      case 'snow':
        return <SnowParticles config={config as typeof WeatherConfigs.snow} intensity={effectiveIntensity} />
      case 'sparkles':
        return <SparkleParticles config={config as typeof WeatherConfigs.sparkles} intensity={effectiveIntensity} />
      case 'leaves':
        return <LeafParticles config={config as typeof WeatherConfigs.leaves} intensity={effectiveIntensity} />
      case 'aurora':
        return <SparkleParticles config={WeatherConfigs.aurora} intensity={effectiveIntensity} />
      default:
        return <SparkleParticles config={WeatherConfigs.sparkles} intensity={effectiveIntensity} />
    }
  }, [weather.particles.type, config, effectiveIntensity])
  
  return (
    <group>
      {renderParticleSystem()}
    </group>
  )
}