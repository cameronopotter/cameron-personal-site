import React, { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Cylinder, RoundedBox, Sphere, Tube } from '@react-three/drei'
import { Group, Vector3, CatmullRomCurve3, Color, MeshStandardMaterial } from 'three'
import { useSpring, animated } from '@react-spring/three'

interface NeonInfrastructureProps {
  visible?: boolean
  intensity?: number
  complexityLevel?: number
}

// Neon Street Light Component
const NeonStreetLight: React.FC<{
  position: [number, number, number]
  color: string
  intensity: number
  flickerSpeed?: number
}> = ({ position, color, intensity, flickerSpeed = 1 }) => {
  const lightRef = useRef<any>(null!)
  const glowRef = useRef<any>(null!)
  
  useFrame((state) => {
    if (lightRef.current && glowRef.current) {
      const time = state.clock.getElapsedTime()
      // Subtle flicker effect
      const flicker = Math.sin(time * flickerSpeed * 8) * 0.1 + 0.9
      const baseIntensity = intensity * flicker
      
      lightRef.current.intensity = baseIntensity * 2
      glowRef.current.material.emissiveIntensity = baseIntensity * 0.6
      
      // Color cycling for dynamic effect
      const hue = (Math.sin(time * 0.2) + 1) * 0.5
      const cycleColor = new Color().setHSL(hue * 0.1 + 0.5, 0.8, 0.6)
      lightRef.current.color = color === '#00FFFF' ? cycleColor : new Color(color)
    }
  })
  
  return (
    <group position={position}>
      {/* Street Light Pole */}
      <Cylinder
        args={[0.05, 0.08, 3, 8]}
        position={[0, 1.5, 0]}
      >
        <meshStandardMaterial
          color="#333333"
          metalness={0.8}
          roughness={0.2}
        />
      </Cylinder>
      
      {/* Light Housing */}
      <RoundedBox
        args={[0.3, 0.2, 0.3]}
        position={[0, 3.2, 0]}
        radius={0.02}
      >
        <meshStandardMaterial
          color="#111111"
          metalness={0.9}
          roughness={0.1}
        />
      </RoundedBox>
      
      {/* Neon Glow Sphere */}
      <Sphere
        ref={glowRef}
        args={[0.15, 16, 12]}
        position={[0, 3.2, 0]}
      >
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={intensity * 0.6}
          transparent
          opacity={0.8}
        />
      </Sphere>
      
      {/* Point Light */}
      <pointLight
        ref={lightRef}
        position={[0, 3.2, 0]}
        color={color}
        intensity={intensity * 2}
        distance={12}
        decay={2}
        castShadow
      />
      
      {/* Ground Glow Effect */}
      <Cylinder
        args={[1.5, 0.5, 0.02, 16]}
        position={[0, 0.01, 0]}
        rotation={[0, 0, 0]}
      >
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={intensity * 0.2}
          transparent
          opacity={0.3}
        />
      </Cylinder>
    </group>
  )
}

// Neon Road Component
const NeonRoad: React.FC<{
  startPoint: [number, number, number]
  endPoint: [number, number, number]
  width?: number
  glowColor?: string
  animated?: boolean
}> = ({ startPoint, endPoint, width = 1.5, glowColor = '#00FFFF', animated = true }) => {
  const roadRef = useRef<Group>(null!)
  
  // Create curve for road
  const curve = useMemo(() => {
    const start = new Vector3(...startPoint)
    const end = new Vector3(...endPoint)
    const middle = new Vector3().lerpVectors(start, end, 0.5)
    middle.y += 0.1 // Slight curve
    
    return new CatmullRomCurve3([start, middle, end])
  }, [startPoint, endPoint])
  
  useFrame((state) => {
    if (roadRef.current && animated) {
      const time = state.clock.getElapsedTime()
      // Gentle pulsing glow
      const pulse = Math.sin(time * 2) * 0.1 + 0.9
      roadRef.current.children.forEach((child: any) => {
        if (child.material?.emissiveIntensity !== undefined) {
          child.material.emissiveIntensity = 0.1 * pulse
        }
      })
    }
  })
  
  return (
    <group ref={roadRef}>
      {/* Main Road Surface */}
      <Tube
        args={[curve, 20, width / 2, 8, false]}
        position={[0, 0, 0]}
      >
        <meshStandardMaterial
          color="#1a1a1a"
          roughness={0.8}
          metalness={0.1}
        />
      </Tube>
      
      {/* Neon Edge Lines */}
      <Tube
        args={[curve, 20, width / 2 + 0.05, 8, false]}
        position={[0, 0.01, 0]}
      >
        <meshStandardMaterial
          color={glowColor}
          emissive={glowColor}
          emissiveIntensity={0.3}
          transparent
          opacity={0.6}
        />
      </Tube>
      
      {/* Center Line */}
      <Tube
        args={[curve, 40, 0.02, 4, false]}
        position={[0, 0.02, 0]}
      >
        <meshStandardMaterial
          color="#FFFF00"
          emissive="#FFFF00"
          emissiveIntensity={0.4}
        />
      </Tube>
    </group>
  )
}

// Holographic Signs Component
const HolographicSign: React.FC<{
  position: [number, number, number]
  text: string
  color: string
  size?: number
}> = ({ position, text, color, size = 1 }) => {
  const signRef = useRef<any>(null!)
  
  useFrame((state) => {
    if (signRef.current) {
      const time = state.clock.getElapsedTime()
      // Floating animation
      signRef.current.position.y = position[1] + Math.sin(time * 1.5) * 0.1
      // Gentle rotation
      signRef.current.rotation.y = Math.sin(time * 0.5) * 0.1
    }
  })
  
  return (
    <group ref={signRef} position={position}>
      {/* Sign Background */}
      <RoundedBox
        args={[text.length * 0.3 * size, 0.8 * size, 0.05]}
        radius={0.02}
      >
        <meshStandardMaterial
          color="#000000"
          transparent
          opacity={0.8}
          emissive={color}
          emissiveIntensity={0.1}
        />
      </RoundedBox>
      
      {/* Holographic Border */}
      <RoundedBox
        args={[text.length * 0.32 * size, 0.82 * size, 0.02]}
        position={[0, 0, 0.01]}
        radius={0.02}
      >
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.5}
          transparent
          opacity={0.3}
        />
      </RoundedBox>
    </group>
  )
}

// Main Neon Infrastructure Component
export const NeonInfrastructure: React.FC<NeonInfrastructureProps> = ({
  visible = true,
  intensity = 1,
  complexityLevel = 3
}) => {
  const groupRef = useRef<Group>(null!)
  
  // Define neon color palette
  const neonColors = [
    '#00FFFF', // Cyan
    '#FF1493', // Deep Pink  
    '#00FF00', // Lime
    '#FF4500', // Orange Red
    '#9400D3', // Violet
    '#FFFF00', // Yellow
  ]
  
  // Street light positions forming paths through the garden
  const streetLightPositions: Array<{ pos: [number, number, number], color: string }> = [
    // Main central path
    { pos: [-15, 0, -10], color: neonColors[0] },
    { pos: [-7, 0, -5], color: neonColors[1] },
    { pos: [0, 0, 0], color: neonColors[2] },
    { pos: [7, 0, 5], color: neonColors[3] },
    { pos: [15, 0, 10], color: neonColors[4] },
    
    // Cross paths
    { pos: [-10, 0, 8], color: neonColors[5] },
    { pos: [-3, 0, 12], color: neonColors[0] },
    { pos: [3, 0, -12], color: neonColors[1] },
    { pos: [10, 0, -8], color: neonColors[2] },
    
    // Perimeter lights
    { pos: [-20, 0, 0], color: neonColors[3] },
    { pos: [20, 0, 0], color: neonColors[4] },
    { pos: [0, 0, -20], color: neonColors[5] },
    { pos: [0, 0, 20], color: neonColors[0] },
  ]
  
  // Road paths
  const roadPaths: Array<{ start: [number, number, number], end: [number, number, number], color: string }> = [
    { start: [-20, 0, -15], end: [20, 0, 15], color: '#00FFFF' },
    { start: [-15, 0, 20], end: [15, 0, -20], color: '#FF1493' },
    { start: [-25, 0, 0], end: [25, 0, 0], color: '#00FF00' },
    { start: [0, 0, -25], end: [0, 0, 25], color: '#FFFF00' },
  ]
  
  // Holographic signs
  const signs = [
    { pos: [-12, 2, -15], text: "CAMERON POTTER", color: '#00FFFF', size: 1.2 },
    { pos: [12, 2, 15], text: "DIGITAL GARDEN", color: '#FF1493', size: 1 },
    { pos: [-15, 2, 12], text: "PROJECTS", color: '#00FF00', size: 0.8 },
    { pos: [15, 2, -12], text: "SKILLS", color: '#FFFF00', size: 0.8 },
  ]
  
  const { scale, opacity } = useSpring({
    scale: visible ? 1 : 0,
    opacity: visible ? intensity : 0,
    config: { tension: 300, friction: 30 }
  })
  
  if (!visible) return null
  
  return (
    <animated.group 
      ref={groupRef} 
      scale={scale as any}
      opacity={opacity as any}
    >
      {/* Street Lights */}
      {streetLightPositions.map((light, index) => (
        <NeonStreetLight
          key={`light-${index}`}
          position={light.pos}
          color={light.color}
          intensity={intensity}
          flickerSpeed={1 + Math.random()}
        />
      ))}
      
      {/* Roads */}
      {complexityLevel > 1 && roadPaths.map((road, index) => (
        <NeonRoad
          key={`road-${index}`}
          startPoint={road.start}
          endPoint={road.end}
          glowColor={road.color}
          animated={true}
        />
      ))}
      
      {/* Holographic Signs */}
      {complexityLevel > 2 && signs.map((sign, index) => (
        <HolographicSign
          key={`sign-${index}`}
          position={sign.pos}
          text={sign.text}
          color={sign.color}
          size={sign.size}
        />
      ))}
      
      {/* Ground Grid Effect */}
      {complexityLevel > 3 && (
        <mesh position={[0, -0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[60, 60, 20, 20]} />
          <meshStandardMaterial
            color="#001122"
            emissive="#00FFFF"
            emissiveIntensity={0.05}
            transparent
            opacity={0.2}
            wireframe
          />
        </mesh>
      )}
      
      {/* Ambient Fog Effect */}
      {complexityLevel > 1 && (
        <mesh position={[0, 1, 0]}>
          <sphereGeometry args={[40, 16, 8]} />
          <meshStandardMaterial
            color="#000033"
            emissive="#0066FF"
            emissiveIntensity={0.02}
            transparent
            opacity={0.1}
          />
        </mesh>
      )}
    </animated.group>
  )
}