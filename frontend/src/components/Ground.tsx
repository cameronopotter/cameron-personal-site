import React, { useMemo, useRef } from 'react'
import { useFrame, useLoader } from '@react-three/fiber'
import { TextureLoader, RepeatWrapping, Color, Mesh } from 'three'
import type { Season, WeatherState, ComplexityLevel } from '@/types'

interface GroundProps {
  size: number
  season: Season
  weather: WeatherState
  complexityLevel: ComplexityLevel
  onClick?: (event: any) => void
}

export const Ground: React.FC<GroundProps> = ({
  size,
  season,
  weather,
  complexityLevel,
  onClick
}) => {
  const meshRef = useRef<Mesh>(null!)

  // Seasonal ground colors
  const groundColor = useMemo(() => {
    const seasonColors = {
      spring: new Color('#4a5d2a'), // Fresh green
      summer: new Color('#3d4f1f'), // Deep green  
      autumn: new Color('#5d4a2a'), // Earthy brown
      winter: new Color('#6b7280')  // Gray-blue
    }
    return seasonColors[season]
  }, [season])

  // Simple animated ground effect
  useFrame((state) => {
    if (meshRef.current && complexityLevel > 2) {
      const time = state.clock.getElapsedTime()
      // Subtle height variation for "breathing" effect
      meshRef.current.position.y = Math.sin(time * 0.5) * 0.01
    }
  })

  return (
    <group onClick={onClick}>
      {/* Main ground plane */}
      <mesh
        ref={meshRef}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, -0.1, 0]}
        receiveShadow
      >
        <planeGeometry args={[size, size, complexityLevel > 1 ? 32 : 8, complexityLevel > 1 ? 32 : 8]} />
        <meshStandardMaterial
          color={groundColor}
          roughness={0.8}
          metalness={0.1}
        />
      </mesh>

      {/* Grid lines for development/navigation aid */}
      {complexityLevel > 2 && (
        <gridHelper
          args={[size, 20, new Color('#4CAF50').multiplyScalar(0.3), new Color('#4CAF50').multiplyScalar(0.1)]}
          position={[0, 0, 0]}
        />
      )}

      {/* Subtle fog/mist effect at ground level */}
      {complexityLevel > 3 && weather.particles.type !== 'rain' && (
        <mesh position={[0, 0.5, 0]}>
          <sphereGeometry args={[size * 0.8, 16, 8]} />
          <meshBasicMaterial
            color={weather.lighting.ambient}
            transparent
            opacity={0.03}
          />
        </mesh>
      )}
    </group>
  )
}