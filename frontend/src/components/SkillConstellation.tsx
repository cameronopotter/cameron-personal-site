import React, { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Text, Line, Sphere } from '@react-three/drei'
import { Group, Vector3, Color } from 'three'
import { useSpring, animated } from '@react-spring/three'
import type { SkillConstellationProps, Skill } from '@/types'

// Individual skill star component
const SkillStar: React.FC<{
  skill: Skill
  isSelected: boolean
  onSelect: (skill: Skill) => void
}> = ({ skill, isSelected, onSelect }) => {
  const meshRef = useRef<any>(null!)
  
  const { scale, emissiveIntensity } = useSpring({
    scale: isSelected ? 1.5 : 1,
    emissiveIntensity: isSelected ? 0.8 : skill.brightness * 0.5,
    config: { tension: 300, friction: 30 }
  })

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.5
    }
  })

  return (
    <animated.group
      position={skill.position}
      scale={scale as any}
      onClick={() => onSelect(skill)}
      onPointerOver={(e) => {
        e.stopPropagation()
        document.body.style.cursor = 'pointer'
      }}
      onPointerOut={() => {
        document.body.style.cursor = 'default'
      }}
    >
      <Sphere
        ref={meshRef}
        args={[0.2, 16, 16]}
      >
        <meshStandardMaterial
          color={new Color().setHSL(skill.proficiency * 0.3, 0.8, 0.6)}
          emissive={new Color().setHSL(skill.proficiency * 0.3, 0.8, 0.3)}
          emissiveIntensity={emissiveIntensity as any}
          transparent
          opacity={0.8}
        />
      </Sphere>
      
      <Text
        position={[0, -0.5, 0]}
        fontSize={0.15}
        color="white"
        anchorX="center"
        anchorY="middle"
        font="/fonts/Inter-Medium.woff"
        maxWidth={2}
        textAlign="center"
      >
        {skill.name}
        <meshStandardMaterial transparent opacity={0.9} />
      </Text>
      
      {isSelected && (
        <Text
          position={[0, -0.8, 0]}
          fontSize={0.1}
          color="#4CAF50"
          anchorX="center"
          anchorY="middle"
          font="/fonts/Inter-Regular.woff"
        >
          {Math.round(skill.proficiency * 100)}% • {skill.experience}y
        </Text>
      )}
    </animated.group>
  )
}

// Connection lines between related skills
const SkillConnections: React.FC<{
  skills: Skill[]
  visible: boolean
}> = ({ skills, visible }) => {
  const connections = useMemo(() => {
    const lines: Array<{ start: Vector3, end: Vector3, opacity: number }> = []
    
    skills.forEach(skill => {
      skill.connections.forEach(connectionId => {
        const connectedSkill = skills.find(s => s.id === connectionId)
        if (connectedSkill) {
          lines.push({
            start: new Vector3(...skill.position),
            end: new Vector3(...connectedSkill.position),
            opacity: Math.min(skill.proficiency, connectedSkill.proficiency) * 0.3
          })
        }
      })
    })
    
    return lines
  }, [skills])

  if (!visible) return null

  return (
    <group>
      {connections.map((connection, index) => (
        <Line
          key={index}
          points={[connection.start, connection.end]}
          color={new Color('#4CAF50')}
          transparent
          opacity={connection.opacity}
          lineWidth={1}
        />
      ))}
    </group>
  )
}

export const SkillConstellation: React.FC<SkillConstellationProps> = ({
  skills,
  selectedSkill,
  onSkillSelect,
  visible
}) => {
  const groupRef = useRef<Group>(null!)

  // Gentle rotation animation
  useFrame((state) => {
    if (groupRef.current && visible) {
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.05
    }
  })

  if (!visible) return null

  return (
    <group ref={groupRef} position={[0, 8, 0]}>
      {/* Connection lines */}
      <SkillConnections skills={skills} visible={visible} />
      
      {/* Skill stars */}
      {skills.map((skill) => (
        <SkillStar
          key={skill.id}
          skill={skill}
          isSelected={selectedSkill?.id === skill.id}
          onSelect={onSkillSelect}
        />
      ))}
      
      {/* Constellation background glow */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[15, 32, 32]} />
        <meshBasicMaterial
          color={new Color('#4CAF50')}
          transparent
          opacity={0.02}
        />
      </mesh>
    </group>
  )
}