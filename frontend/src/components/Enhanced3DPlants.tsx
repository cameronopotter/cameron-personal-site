import React, { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Sphere, Cylinder, Cone, Torus, Text } from '@react-three/drei'
import { Group, Vector3, Color, MathUtils } from 'three'
import { useSpring, animated } from '@react-spring/three'

interface Enhanced3DPlantsProps {
  position: [number, number, number]
  growthStage: number // 0-1, determines plant size and complexity
  plantType: 'tree' | 'flower' | 'bush' | 'vine' | 'succulent' | 'grass'
  health: number // 0-1, affects colors and fullness
  season: 'spring' | 'summer' | 'autumn' | 'winter'
  isSelected: boolean
  onInteract?: () => void
  projectName?: string
  techStack?: string[]
}

// Dramatically Enhanced Leaf Component
const Leaf: React.FC<{
  position: [number, number, number]
  rotation: [number, number, number]
  scale: number
  color: string
  season: string
}> = ({ position, rotation, scale, color, season }) => {
  const meshRef = useRef<any>(null!)
  
  useFrame((state) => {
    if (meshRef.current) {
      const time = state.clock.getElapsedTime()
      // More natural leaf movement
      meshRef.current.rotation.z = rotation[2] + Math.sin(time * 2 + position[0]) * 0.15
      meshRef.current.rotation.x = rotation[0] + Math.cos(time * 1.5 + position[1]) * 0.1
      
      // Subtle floating
      meshRef.current.position.y = position[1] + Math.sin(time + position[0] * 2) * 0.02
    }
  })
  
  // Seasonal color modifications
  const getSeasonalColor = (baseColor: string, season: string): string => {
    const color = new Color(baseColor)
    
    switch (season) {
      case 'autumn':
        return color.lerp(new Color('#FF5722'), 0.6).getHexString()
      case 'winter':
        return color.lerp(new Color('#90A4AE'), 0.4).getHexString()
      case 'spring':
        return color.lerp(new Color('#8BC34A'), 0.3).getHexString()
      default:
        return baseColor
    }
  }
  
  return (
    <group ref={meshRef} position={position} rotation={rotation} scale={scale}>
      {/* More realistic leaf shape */}
      <mesh>
        <sphereGeometry args={[0.4, 10, 8]} />
        <meshStandardMaterial
          color={getSeasonalColor(color, season)}
          transparent
          opacity={season === 'winter' ? 0.6 : 0.85}
          roughness={0.7}
          metalness={0.1}
        />
      </mesh>
      
      {/* Leaf detail with lighter center */}
      <mesh>
        <sphereGeometry args={[0.2, 8, 6]} />
        <meshStandardMaterial
          color={new Color(getSeasonalColor(color, season)).lerp(new Color('#FFFFFF'), 0.3)}
          transparent
          opacity={0.4}
        />
      </mesh>
      
      {/* Subtle glow for neon effect */}
      <mesh>
        <sphereGeometry args={[0.5, 8, 6]} />
        <meshStandardMaterial
          color="#00FF88"
          emissive="#00FF88"
          emissiveIntensity={0.05}
          transparent
          opacity={0.1}
        />
      </mesh>
    </group>
  )
}

// Dramatically Enhanced Tree Component
const TreePlant: React.FC<{
  growthStage: number
  health: number
  season: string
  position: [number, number, number]
}> = ({ growthStage, health, season, position }) => {
  const groupRef = useRef<Group>(null!)
  
  // Much larger, more impressive trees
  const trunkHeight = 2 + growthStage * 4 // Doubled height
  const canopySize = 1 + growthStage * 2.5 // Larger canopy
  const branchCount = Math.floor(5 + growthStage * 8) // More branches
  
  const branches = useMemo(() => {
    const branchArray = []
    for (let i = 0; i < branchCount; i++) {
      const angle = (i / branchCount) * Math.PI * 2
      const height = trunkHeight * 0.5 + Math.random() * trunkHeight * 0.4
      const radius = 0.4 + Math.random() * 0.6
      const branchLength = 0.8 + Math.random() * 1.2
      
      branchArray.push({
        angle,
        height,
        radius,
        length: branchLength,
        leaves: Math.floor(4 + Math.random() * 6) // More leaves
      })
    }
    return branchArray
  }, [growthStage, branchCount, trunkHeight])
  
  useFrame((state) => {
    if (groupRef.current) {
      const time = state.clock.getElapsedTime()
      // More dramatic swaying for larger trees
      groupRef.current.rotation.y = Math.sin(time * 0.3) * 0.08
      groupRef.current.rotation.x = Math.sin(time * 0.4) * 0.06
      groupRef.current.rotation.z = Math.cos(time * 0.5) * 0.05
      
      // Breathing effect
      const scale = 1 + Math.sin(time * 0.8) * 0.02
      groupRef.current.scale.setScalar(scale)
    }
  })
  
  return (
    <group ref={groupRef} position={position}>
      {/* Enhanced Trunk with bark texture */}
      <Cylinder
        args={[0.15 * growthStage, 0.25 * growthStage, trunkHeight, 12]}
        position={[0, trunkHeight / 2, 0]}
      >
        <meshStandardMaterial 
          color="#654321" 
          roughness={0.9}
          metalness={0.1}
          // Add bark-like normal map effect through color variation
        />
      </Cylinder>
      
      {/* Trunk detail rings */}
      {Array.from({ length: Math.floor(trunkHeight / 0.8) }).map((_, index) => (
        <mesh
          key={`ring-${index}`}
          position={[0, index * 0.8 + 0.4, 0]}
        >
          <torusGeometry args={[0.16 * growthStage, 0.02, 6, 12]} />
          <meshStandardMaterial color="#5D4037" roughness={0.95} />
        </mesh>
      ))}
      
      {/* Branches and leaves */}
      {branches.map((branch, index) => (
        <group key={index}>
          {/* Enhanced Branch */}
          <Cylinder
            args={[0.03, 0.08, branch.length, 8]}
            position={[
              Math.cos(branch.angle) * branch.radius,
              branch.height,
              Math.sin(branch.angle) * branch.radius
            ]}
            rotation={[
              Math.PI / 2 + (Math.random() - 0.5) * 0.6,
              branch.angle,
              (Math.random() - 0.5) * 0.4
            ]}
          >
            <meshStandardMaterial 
              color="#8D6E63" 
              roughness={0.85}
              metalness={0.05}
            />
          </Cylinder>
          
          {/* Leaves on branch */}
          {Array.from({ length: branch.leaves }).map((_, leafIndex) => {
            const leafPos: [number, number, number] = [
              Math.cos(branch.angle) * (branch.radius + 0.2),
              branch.height + 0.1,
              Math.sin(branch.angle) * (branch.radius + 0.2)
            ]
            
            return (
              <Leaf
                key={leafIndex}
                position={leafPos}
                rotation={[Math.random() * 0.8, Math.random() * Math.PI * 2, Math.random() * 0.8]}
                scale={0.8 + Math.random() * 0.6} // Larger leaves
                color={season === 'autumn' ? '#FF5722' : '#4CAF50'}
                season={season}
              />
            )
          })}
        </group>
      ))}
      
      {/* Multi-layered canopy for depth */}
      {Array.from({ length: 3 }).map((_, layer) => {
        const layerSize = canopySize * (0.8 + layer * 0.2)
        const layerHeight = trunkHeight + canopySize * 0.6 + layer * 0.3
        
        return (
          <Sphere
            key={`canopy-${layer}`}
            args={[layerSize, 16, 12]}
            position={[
              (Math.random() - 0.5) * 0.4,
              layerHeight,
              (Math.random() - 0.5) * 0.4
            ]}
          >
            <meshStandardMaterial
              color={
                season === 'autumn' ? 
                  (layer === 0 ? '#FF5722' : layer === 1 ? '#FF8A65' : '#FFAB91') :
                season === 'winter' ? 
                  (layer === 0 ? '#81C784' : layer === 1 ? '#A5D6A7' : '#C8E6C9') :
                  (layer === 0 ? '#2E7D32' : layer === 1 ? '#4CAF50' : '#66BB6A')
              }
              transparent
              opacity={(season === 'winter' ? 0.5 : 0.8) - layer * 0.1}
              roughness={0.6}
              metalness={0.1}
            />
          </Sphere>
        )
      })}
      
      {/* Neon glow effect for cyberpunk theme */}
      <Sphere
        args={[canopySize * 1.2, 12, 8]}
        position={[0, trunkHeight + canopySize * 0.7, 0]}
      >
        <meshStandardMaterial
          color="#00FF88"
          emissive="#00FF88"
          emissiveIntensity={0.1}
          transparent
          opacity={0.15}
        />
      </Sphere>
    </group>
  )
}

// Dramatically Enhanced Flower Component  
const FlowerPlant: React.FC<{
  growthStage: number
  health: number
  season: string
  position: [number, number, number]
}> = ({ growthStage, health, season, position }) => {
  const groupRef = useRef<Group>(null!)
  
  // Much more impressive flowers
  const stemHeight = 1 + growthStage * 2.5 // Taller stems
  const flowerSize = 0.4 + growthStage * 0.6 // Larger flowers  
  const petalCount = 6 + Math.floor(growthStage * 4) // More petals
  
  useFrame((state) => {
    if (groupRef.current) {
      const time = state.clock.getElapsedTime()
      // More dynamic flower movement
      groupRef.current.rotation.z = Math.sin(time * 1.2) * 0.15
      groupRef.current.rotation.y = Math.cos(time * 0.8) * 0.05
      
      // Gentle height bobbing
      groupRef.current.position.y = position[1] + Math.sin(time * 1.5) * 0.05
    }
  })
  
  return (
    <group ref={groupRef} position={position}>
      {/* Enhanced Stem with texture */}
      <Cylinder
        args={[0.04, 0.06, stemHeight, 10]}
        position={[0, stemHeight / 2, 0]}
      >
        <meshStandardMaterial 
          color="#2E7D32" 
          roughness={0.7}
          metalness={0.1}
        />
      </Cylinder>
      
      {/* Stem highlights */}
      <Cylinder
        args={[0.035, 0.055, stemHeight * 0.9, 8]}
        position={[0, stemHeight / 2, 0]}
      >
        <meshStandardMaterial 
          color="#4CAF50" 
          transparent
          opacity={0.6}
        />
      </Cylinder>
      
      {/* Enhanced Flower center with layers */}
      <Sphere
        args={[flowerSize * 0.4, 12, 8]}
        position={[0, stemHeight, 0]}
      >
        <meshStandardMaterial 
          color="#FFC107" 
          emissive="#FFD54F" 
          emissiveIntensity={0.3}
          roughness={0.3}
          metalness={0.2}
        />
      </Sphere>
      
      {/* Center detail */}
      <Sphere
        args={[flowerSize * 0.2, 8, 6]}
        position={[0, stemHeight + 0.05, 0]}
      >
        <meshStandardMaterial 
          color="#FF8F00" 
          emissive="#FF8F00" 
          emissiveIntensity={0.4}
        />
      </Sphere>
      
      {/* Pistil effects */}
      {Array.from({ length: 8 }).map((_, i) => {
        const angle = (i / 8) * Math.PI * 2
        const radius = flowerSize * 0.15
        return (
          <Sphere
            key={`pistil-${i}`}
            args={[0.02, 6, 4]}
            position={[
              Math.cos(angle) * radius,
              stemHeight + 0.08,
              Math.sin(angle) * radius
            ]}
          >
            <meshStandardMaterial color="#FFE082" />
          </Sphere>
        )
      })}
      
      {/* Enhanced Layered Petals */}
      {Array.from({ length: petalCount }).map((_, index) => {
        const angle = (index / petalCount) * Math.PI * 2
        const petalRadius = flowerSize * 0.9
        
        return (
          <group key={`petal-group-${index}`}>
            {/* Outer petal layer */}
            <mesh
              position={[
                Math.cos(angle) * petalRadius * 0.8,
                stemHeight + 0.02,
                Math.sin(angle) * petalRadius * 0.8
              ]}
              rotation={[Math.PI / 6, angle, 0]}
            >
              <sphereGeometry args={[flowerSize * 0.7, 8, 6]} />
              <meshStandardMaterial
                color={season === 'spring' ? '#E91E63' : season === 'summer' ? '#FF5722' : '#9C27B0'}
                transparent
                opacity={0.85}
                roughness={0.2}
                metalness={0.1}
              />
            </mesh>
            
            {/* Inner petal layer */}
            <mesh
              position={[
                Math.cos(angle) * petalRadius * 0.6,
                stemHeight + 0.01,
                Math.sin(angle) * petalRadius * 0.6
              ]}
              rotation={[Math.PI / 8, angle, 0]}
            >
              <sphereGeometry args={[flowerSize * 0.5, 6, 4]} />
              <meshStandardMaterial
                color={new Color(season === 'spring' ? '#E91E63' : season === 'summer' ? '#FF5722' : '#9C27B0').lerp(new Color('#FFFFFF'), 0.3)}
                transparent
                opacity={0.7}
              />
            </mesh>
            
            {/* Petal glow effect */}
            <mesh
              position={[
                Math.cos(angle) * petalRadius * 0.8,
                stemHeight + 0.02,
                Math.sin(angle) * petalRadius * 0.8
              ]}
            >
              <sphereGeometry args={[flowerSize * 0.8, 6, 4]} />
              <meshStandardMaterial
                color="#FF1493"
                emissive="#FF1493"
                emissiveIntensity={0.1}
                transparent
                opacity={0.2}
              />
            </mesh>
          </group>
        )
      })}
      
      {/* Enhanced Leaves with variety */}
      {Array.from({ length: 5 }).map((_, index) => {
        const leafHeight = stemHeight * (0.2 + index * 0.15)
        const leafAngle = (index * Math.PI * 2) / 5 + Math.random() * 0.5
        
        return (
          <Leaf
            key={index}
            position={[
              Math.cos(leafAngle) * (0.4 + Math.random() * 0.2),
              leafHeight,
              Math.sin(leafAngle) * (0.4 + Math.random() * 0.2)
            ]}
            rotation={[Math.PI / 2 + (Math.random() - 0.5) * 0.4, leafAngle, (Math.random() - 0.5) * 0.3]}
            scale={0.6 + Math.random() * 0.4} // Larger leaves
            color="#4CAF50"
            season={season}
          />
        )
      })}
    </group>
  )
}

// Bush Component
const BushPlant: React.FC<{
  growthStage: number
  health: number
  season: string
  position: [number, number, number]
}> = ({ growthStage, health, season, position }) => {
  const groupRef = useRef<Group>(null!)
  
  const bushSize = 0.4 + growthStage * 0.8
  const branchCount = Math.floor(5 + growthStage * 8)
  
  const branches = useMemo(() => {
    return Array.from({ length: branchCount }).map(() => ({
      position: [
        (Math.random() - 0.5) * bushSize * 1.5,
        Math.random() * bushSize,
        (Math.random() - 0.5) * bushSize * 1.5
      ] as [number, number, number],
      size: 0.1 + Math.random() * 0.2,
      leaves: Math.floor(2 + Math.random() * 3)
    }))
  }, [bushSize, branchCount])
  
  useFrame((state) => {
    if (groupRef.current) {
      const time = state.clock.getElapsedTime()
      groupRef.current.rotation.y = Math.sin(time * 0.1) * 0.05
    }
  })
  
  return (
    <group ref={groupRef} position={position}>
      {branches.map((branch, index) => (
        <group key={index}>
          {/* Branch sphere */}
          <Sphere
            args={[branch.size, 8, 6]}
            position={branch.position}
          >
            <meshStandardMaterial
              color={season === 'autumn' ? '#FF7043' : '#4CAF50'}
              transparent
              opacity={0.9}
            />
          </Sphere>
          
          {/* Leaves around branch */}
          {Array.from({ length: branch.leaves }).map((_, leafIndex) => (
            <Leaf
              key={leafIndex}
              position={[
                branch.position[0] + (Math.random() - 0.5) * 0.4,
                branch.position[1] + (Math.random() - 0.5) * 0.2,
                branch.position[2] + (Math.random() - 0.5) * 0.4
              ]}
              rotation={[Math.random() * Math.PI, Math.random() * Math.PI * 2, Math.random() * Math.PI]}
              scale={0.3 + Math.random() * 0.2}
              color="#4CAF50"
              season={season}
            />
          ))}
        </group>
      ))}
    </group>
  )
}

// Succulent Component
const SucculentPlant: React.FC<{
  growthStage: number
  health: number
  season: string
  position: [number, number, number]
}> = ({ growthStage, health, season, position }) => {
  const groupRef = useRef<Group>(null!)
  
  const baseSize = 0.3 + growthStage * 0.4
  const layerCount = Math.floor(2 + growthStage * 3)
  
  useFrame((state) => {
    if (groupRef.current) {
      const time = state.clock.getElapsedTime()
      groupRef.current.rotation.y = time * 0.1
    }
  })
  
  return (
    <group ref={groupRef} position={position}>
      {Array.from({ length: layerCount }).map((_, layer) => {
        const layerSize = baseSize * (1 - layer * 0.15)
        const petalCount = 6 + layer * 2
        
        return (
          <group key={layer} position={[0, layer * 0.1, 0]}>
            {Array.from({ length: petalCount }).map((_, petal) => {
              const angle = (petal / petalCount) * Math.PI * 2
              const radius = layerSize * 0.8
              
              return (
                <mesh
                  key={petal}
                  position={[
                    Math.cos(angle) * radius,
                    0,
                    Math.sin(angle) * radius
                  ]}
                  rotation={[Math.PI / 4, angle, 0]}
                >
                  <sphereGeometry args={[layerSize * 0.3, 6, 4]} />
                  <meshStandardMaterial
                    color={health > 0.7 ? '#4CAF50' : '#81C784'}
                    roughness={0.3}
                  />
                </mesh>
              )
            })}
          </group>
        )
      })}
    </group>
  )
}

// Vine Component
const VinePlant: React.FC<{
  growthStage: number
  health: number
  season: string
  position: [number, number, number]
}> = ({ growthStage, health, season, position }) => {
  const groupRef = useRef<Group>(null!)
  
  const vineLength = 1 + growthStage * 2
  const segments = Math.floor(5 + growthStage * 8)
  
  const vinePoints = useMemo(() => {
    return Array.from({ length: segments }).map((_, index) => {
      const t = index / segments
      const height = t * vineLength
      const radius = Math.sin(t * Math.PI * 3) * 0.5
      const angle = t * Math.PI * 4
      
      return [
        Math.cos(angle) * radius,
        height,
        Math.sin(angle) * radius
      ] as [number, number, number]
    })
  }, [vineLength, segments])
  
  useFrame((state) => {
    if (groupRef.current) {
      const time = state.clock.getElapsedTime()
      groupRef.current.rotation.y = time * 0.05
    }
  })
  
  return (
    <group ref={groupRef} position={position}>
      {vinePoints.map((point, index) => (
        <group key={index}>
          {/* Vine segment */}
          <Cylinder
            args={[0.02, 0.03, 0.2, 6]}
            position={point}
            rotation={[Math.random() * 0.3, Math.random() * Math.PI, Math.random() * 0.3]}
          >
            <meshStandardMaterial color="#2E7D32" />
          </Cylinder>
          
          {/* Occasional leaves */}
          {index % 2 === 0 && (
            <Leaf
              position={[point[0] + 0.2, point[1], point[2]]}
              rotation={[Math.PI / 2, Math.random() * Math.PI * 2, 0]}
              scale={0.3 + Math.random() * 0.2}
              color="#4CAF50"
              season={season}
            />
          )}
        </group>
      ))}
    </group>
  )
}

// Main Enhanced 3D Plants Component
export const Enhanced3DPlants: React.FC<Enhanced3DPlantsProps> = ({
  position,
  growthStage,
  plantType,
  health,
  season,
  isSelected,
  onInteract,
  projectName,
  techStack = []
}) => {
  const groupRef = useRef<Group>(null!)
  
  const { scale, emissiveIntensity } = useSpring({
    scale: isSelected ? 1.2 : 1,
    emissiveIntensity: isSelected ? 0.3 : 0.1,
    config: { tension: 300, friction: 30 }
  })
  
  useFrame((state) => {
    if (groupRef.current && isSelected) {
      groupRef.current.position.y = position[1] + Math.sin(state.clock.getElapsedTime() * 2) * 0.1
    }
  })
  
  const renderPlant = () => {
    const commonProps = { growthStage, health, season, position: [0, 0, 0] as [number, number, number] }
    
    switch (plantType) {
      case 'tree':
        return <TreePlant {...commonProps} />
      case 'flower':
        return <FlowerPlant {...commonProps} />
      case 'bush':
        return <BushPlant {...commonProps} />
      case 'succulent':
        return <SucculentPlant {...commonProps} />
      case 'vine':
        return <VinePlant {...commonProps} />
      case 'grass':
        return <BushPlant {...commonProps} /> // Use bush as grass for now
      default:
        return <TreePlant {...commonProps} />
    }
  }
  
  return (
    <animated.group
      ref={groupRef}
      position={position}
      scale={scale as any}
      onClick={onInteract}
      onPointerOver={(e) => {
        e.stopPropagation()
        document.body.style.cursor = 'pointer'
      }}
      onPointerOut={() => {
        document.body.style.cursor = 'default'
      }}
    >
      {renderPlant()}
      
      {/* Project name label */}
      {projectName && isSelected && (
        <Text
          position={[0, 2 + growthStage * 2, 0]}
          fontSize={0.3}
          color="#4CAF50"
          anchorX="center"
          anchorY="middle"
          font="/fonts/Inter-Bold.woff"
        >
          {projectName}
          <meshStandardMaterial 
            transparent 
            opacity={0.9}
            emissive="#4CAF50"
            emissiveIntensity={emissiveIntensity as any}
          />
        </Text>
      )}
      
      {/* Tech stack indicators */}
      {techStack.length > 0 && isSelected && (
        <group position={[0, 1.5 + growthStage * 2, 0]}>
          {techStack.slice(0, 3).map((tech, index) => (
            <Text
              key={tech}
              position={[(index - 1) * 0.8, -0.4, 0]}
              fontSize={0.15}
              color="white"
              anchorX="center"
              anchorY="middle"
              font="/fonts/Inter-Medium.woff"
            >
              {tech}
              <meshStandardMaterial transparent opacity={0.8} />
            </Text>
          ))}
        </group>
      )}
      
      {/* Growth stage indicator (rings around base) */}
      {Array.from({ length: Math.floor(growthStage * 5) }).map((_, index) => (
        <Torus
          key={index}
          args={[0.3 + index * 0.2, 0.02, 8, 16]}
          position={[0, 0.1, 0]}
          rotation={[Math.PI / 2, 0, 0]}
        >
          <meshStandardMaterial
            color="#4CAF50"
            transparent
            opacity={0.3 - index * 0.05}
            emissive="#4CAF50"
            emissiveIntensity={0.1}
          />
        </Torus>
      ))}
    </animated.group>
  )
}