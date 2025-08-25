import React, { useRef, useMemo, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import { Points, PointMaterial, Sphere } from '@react-three/drei'
import { Group, Vector3, Color, BufferGeometry, BufferAttribute, AdditiveBlending, Texture, TextureLoader } from 'three'
import { useSpring, animated } from '@react-spring/three'

interface StarryNightSkyProps {
  visible: boolean
  timeOfDay: 'day' | 'evening' | 'night' | 'dawn'
  season: 'spring' | 'summer' | 'autumn' | 'winter'
  weather: {
    type: string
    intensity: number
  }
}

// Individual twinkling star component
const TwinklingStar: React.FC<{
  position: [number, number, number]
  size: number
  brightness: number
  color: string
  twinkleSpeed: number
}> = ({ position, size, brightness, color, twinkleSpeed }) => {
  const meshRef = useRef<any>(null!)
  
  useFrame((state) => {
    if (meshRef.current) {
      const time = state.clock.getElapsedTime()
      const twinkle = Math.sin(time * twinkleSpeed) * 0.3 + 0.7
      meshRef.current.material.opacity = brightness * twinkle
      meshRef.current.material.size = size * (0.8 + twinkle * 0.4)
    }
  })

  return (
    <Points ref={meshRef} positions={[position]}>
      <PointMaterial
        transparent
        color={color}
        size={size}
        sizeAttenuation={false}
        blending={AdditiveBlending}
        opacity={brightness}
      />
    </Points>
  )
}

// Nebula background component
const NebulaBackground: React.FC<{
  visible: boolean
  colors: string[]
  intensity: number
}> = ({ visible, colors, intensity }) => {
  const meshRef = useRef<any>(null!)
  const cloudPositions = useMemo(() => {
    const positions: [number, number, number][] = []
    for (let i = 0; i < 15; i++) {
      const angle = (i / 15) * Math.PI * 2
      const radius = 80 + Math.random() * 40
      const height = (Math.random() - 0.5) * 30
      positions.push([
        Math.cos(angle) * radius,
        height,
        Math.sin(angle) * radius
      ])
    }
    return positions
  }, [])

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.02
    }
  })

  if (!visible) return null

  return (
    <group ref={meshRef}>
      {cloudPositions.map((position, index) => (
        <mesh key={index} position={position}>
          <sphereGeometry args={[8 + Math.random() * 12, 16, 16]} />
          <meshBasicMaterial
            color={new Color(colors[index % colors.length])}
            transparent
            opacity={intensity * 0.15 * (0.5 + Math.random() * 0.5)}
          />
        </mesh>
      ))}
    </group>
  )
}

// Aurora effect for special weather conditions
const AuroraEffect: React.FC<{
  visible: boolean
  colors: string[]
  intensity: number
}> = ({ visible, colors, intensity }) => {
  const meshRef = useRef<any>(null!)

  useFrame((state) => {
    if (meshRef.current) {
      const time = state.clock.getElapsedTime()
      meshRef.current.material.opacity = intensity * 0.4 * (Math.sin(time * 0.5) * 0.3 + 0.7)
      meshRef.current.rotation.y = time * 0.1
    }
  })

  if (!visible) return null

  return (
    <mesh ref={meshRef} position={[0, 30, 0]}>
      <cylinderGeometry args={[120, 120, 40, 64, 1, true]} />
      <meshBasicMaterial
        color={new Color(colors[0])}
        transparent
        opacity={intensity * 0.4}
        side={2}
      />
    </mesh>
  )
}

// Main starry night sky component
export const StarryNightSky: React.FC<StarryNightSkyProps> = ({
  visible,
  timeOfDay,
  season,
  weather
}) => {
  const groupRef = useRef<Group>(null!)
  
  // Generate star field based on season and time
  const stars = useMemo(() => {
    const starCount = timeOfDay === 'night' ? 2000 : (timeOfDay === 'evening' ? 800 : 200)
    const starsArray: Array<{
      position: [number, number, number]
      size: number
      brightness: number
      color: string
      twinkleSpeed: number
    }> = []

    // Seasonal color variations
    const seasonalColors = {
      spring: ['#ffffff', '#e3f2fd', '#f8bbd9', '#e1f5fe'],
      summer: ['#fff59d', '#ffffff', '#ffecb3', '#f3e5f5'],
      autumn: ['#ffab91', '#ffffff', '#ffd54f', '#ffcc02'],
      winter: ['#e1f5fe', '#ffffff', '#b3e5fc', '#81d4fa']
    }

    const colors = seasonalColors[season]

    for (let i = 0; i < starCount; i++) {
      // Create dome-like distribution
      const phi = Math.acos(1 - Math.random()) // Uniform distribution on sphere
      const theta = Math.random() * Math.PI * 2
      const radius = 150 + Math.random() * 100

      const x = Math.sin(phi) * Math.cos(theta) * radius
      const y = Math.abs(Math.cos(phi) * radius) + 20 // Keep stars above horizon
      const z = Math.sin(phi) * Math.sin(theta) * radius

      starsArray.push({
        position: [x, y, z],
        size: 0.5 + Math.random() * 2,
        brightness: 0.3 + Math.random() * 0.7,
        color: colors[Math.floor(Math.random() * colors.length)],
        twinkleSpeed: 1 + Math.random() * 3
      })
    }

    return starsArray
  }, [timeOfDay, season])

  // Constellation patterns for skills
  const constellations = useMemo(() => {
    const patterns = [
      // Frontend constellation (Orion-like pattern)
      {
        name: 'Frontend',
        stars: [
          [40, 60, -20], [45, 65, -25], [35, 55, -15],
          [50, 70, -30], [30, 50, -10], [55, 75, -35]
        ],
        color: '#4CAF50'
      },
      // Backend constellation (Big Dipper-like pattern)
      {
        name: 'Backend',
        stars: [
          [-40, 60, 20], [-45, 65, 25], [-35, 55, 15],
          [-50, 70, 30], [-30, 50, 10], [-55, 62, 35], [-25, 58, 8]
        ],
        color: '#2196F3'
      },
      // Languages constellation (Cassiopeia-like pattern)
      {
        name: 'Languages',
        stars: [
          [0, 80, -40], [10, 85, -45], [20, 80, -50],
          [-10, 85, -35], [-20, 80, -30]
        ],
        color: '#FF9800'
      },
      // Tools constellation (Southern Cross-like pattern)
      {
        name: 'Tools',
        stars: [
          [20, 45, 40], [25, 50, 45], [15, 40, 35],
          [30, 55, 50], [10, 35, 30]
        ],
        color: '#9C27B0'
      }
    ]

    return patterns
  }, [])

  // Night sky opacity based on time of day
  const { opacity } = useSpring({
    opacity: timeOfDay === 'night' ? 1 : (timeOfDay === 'evening' ? 0.7 : 0.3),
    config: { duration: 2000 }
  })

  // Nebula colors based on season and weather
  const nebulaColors = useMemo(() => {
    const baseColors = {
      spring: ['#e8f5e8', '#f3e5f5', '#e3f2fd'],
      summer: ['#fff3e0', '#f9fbe7', '#e8eaf6'],
      autumn: ['#fff8e1', '#fce4ec', '#efebe9'],
      winter: ['#e0f2f1', '#e1f5fe', '#f3e5f5']
    }

    if (weather.type === 'aurora') {
      return ['#4CAF50', '#2196F3', '#9C27B0', '#FF4081']
    }

    return baseColors[season]
  }, [season, weather.type])

  useFrame((state) => {
    if (groupRef.current) {
      // Very slow rotation of the entire sky
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.005
    }
  })

  if (!visible) return null

  return (
    <animated.group ref={groupRef} position={[0, 0, 0]} opacity={opacity as any}>
      {/* Main star field */}
      {stars.map((star, index) => (
        <TwinklingStar
          key={index}
          position={star.position}
          size={star.size}
          brightness={star.brightness}
          color={star.color}
          twinkleSpeed={star.twinkleSpeed}
        />
      ))}

      {/* Constellation patterns */}
      {constellations.map((constellation, index) => (
        <group key={index}>
          {constellation.stars.map((position, starIndex) => (
            <TwinklingStar
              key={`${index}-${starIndex}`}
              position={position as [number, number, number]}
              size={2}
              brightness={0.8}
              color={constellation.color}
              twinkleSpeed={0.5}
            />
          ))}
        </group>
      ))}

      {/* Nebula background */}
      <NebulaBackground
        visible={timeOfDay === 'night'}
        colors={nebulaColors}
        intensity={weather.intensity * 0.5}
      />

      {/* Aurora effects for special weather */}
      <AuroraEffect
        visible={weather.type === 'aurora' && timeOfDay === 'night'}
        colors={['#4CAF50', '#2196F3', '#9C27B0']}
        intensity={weather.intensity}
      />

      {/* Milky Way effect */}
      {timeOfDay === 'night' && (
        <mesh position={[0, 40, 0]} rotation={[0, Math.PI / 4, Math.PI / 12]}>
          <cylinderGeometry args={[200, 200, 5, 64, 1, true]} />
          <meshBasicMaterial
            color={new Color('#f5f5dc')}
            transparent
            opacity={0.1}
            side={2}
          />
        </mesh>
      )}

      {/* Moon */}
      {(timeOfDay === 'night' || timeOfDay === 'evening') && (
        <mesh position={[80, 70, -60]}>
          <sphereGeometry args={[8, 32, 32]} />
          <meshBasicMaterial
            color={new Color('#f5f5dc')}
            emissive={new Color('#f5f5dc')}
            emissiveIntensity={0.3}
          />
        </mesh>
      )}
    </animated.group>
  )
}