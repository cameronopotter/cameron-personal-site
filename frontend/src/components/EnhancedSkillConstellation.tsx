import React, { useRef, useMemo, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import { Text, Line, Sphere } from '@react-three/drei'
import { Group, Vector3, Color, BufferGeometry, BufferAttribute, AdditiveBlending } from 'three'
import { useSpring, animated } from '@react-spring/three'

interface Skill {
  id: string
  name: string
  category: string
  level: number // 0-1
  experience: number // years
  position: [number, number, number]
  connections: string[]
}

interface ConstellationPattern {
  name: string
  stars: Array<{
    skill: Skill
    position: [number, number, number]
  }>
  connections: Array<[number, number]> // indices of connected stars
  color: string
  constellation: string // ASCII art pattern
}

interface EnhancedSkillConstellationProps {
  visible: boolean
  selectedSkill: Skill | null
  onSkillSelect: (skill: Skill) => void
  season: 'spring' | 'summer' | 'autumn' | 'winter'
  timeOfDay: 'day' | 'evening' | 'night' | 'dawn'
}

// Cameron Potter's actual skills with realistic levels
const cameronSkills: Skill[] = [
  // Backend/Languages - Major constellation
  {
    id: 'php',
    name: 'PHP',
    category: 'backend',
    level: 0.9,
    experience: 4,
    position: [-15, 45, -30],
    connections: ['laravel', 'mysql', 'composer']
  },
  {
    id: 'laravel', 
    name: 'Laravel',
    category: 'backend',
    level: 0.9,
    experience: 3,
    position: [-12, 50, -35],
    connections: ['php', 'mysql', 'eloquent']
  },
  {
    id: 'javascript',
    name: 'JavaScript',
    category: 'frontend',
    level: 0.85,
    experience: 5,
    position: [15, 50, -25],
    connections: ['vue', 'react', 'node']
  },
  {
    id: 'vue',
    name: 'Vue.js',
    category: 'frontend', 
    level: 0.85,
    experience: 3,
    position: [18, 55, -30],
    connections: ['javascript', 'vuex', 'nuxt']
  },
  {
    id: 'python',
    name: 'Python',
    category: 'backend',
    level: 0.8,
    experience: 3,
    position: [-8, 40, -40],
    connections: ['django', 'flask', 'pandas']
  },
  
  // Frontend constellation
  {
    id: 'react',
    name: 'React',
    category: 'frontend',
    level: 0.8,
    experience: 2,
    position: [12, 45, -20],
    connections: ['javascript', 'jsx', 'hooks']
  },
  {
    id: 'css',
    name: 'CSS3',
    category: 'frontend',
    level: 0.85,
    experience: 5,
    position: [20, 40, -15],
    connections: ['sass', 'responsive', 'flexbox']
  },
  {
    id: 'html',
    name: 'HTML5', 
    category: 'frontend',
    level: 0.9,
    experience: 5,
    position: [25, 35, -20],
    connections: ['css', 'semantic', 'accessibility']
  },
  
  // Database/Tools constellation
  {
    id: 'mysql',
    name: 'MySQL',
    category: 'database',
    level: 0.8,
    experience: 4,
    position: [-20, 35, -45],
    connections: ['php', 'laravel', 'sql']
  },
  {
    id: 'git',
    name: 'Git',
    category: 'tools',
    level: 0.85,
    experience: 4,
    position: [0, 60, -50],
    connections: ['github', 'version-control', 'collaboration']
  },
  {
    id: 'docker',
    name: 'Docker',
    category: 'tools',
    level: 0.7,
    experience: 2,
    position: [5, 35, -55],
    connections: ['containerization', 'deployment', 'devops']
  },
  
  // Systems/Languages
  {
    id: 'java',
    name: 'Java',
    category: 'backend',
    level: 0.7,
    experience: 2,
    position: [-25, 55, -25],
    connections: ['oop', 'spring', 'jvm']
  },
  {
    id: 'cpp',
    name: 'C++',
    category: 'systems',
    level: 0.65,
    experience: 1.5,
    position: [-30, 30, -35],
    connections: ['memory-management', 'performance', 'algorithms']
  },
  {
    id: 'csharp',
    name: 'C#',
    category: 'backend',
    level: 0.6,
    experience: 1,
    position: [-35, 40, -30],
    connections: ['dotnet', 'oop', 'microsoft']
  }
]

// Create constellation patterns based on skill categories
const createConstellationPatterns = (skills: Skill[]): ConstellationPattern[] => {
  const categories = {
    backend: { name: 'The Craftsman', color: '#4CAF50', constellation: '⚒️' },
    frontend: { name: 'The Artist', color: '#2196F3', constellation: '🎨' },
    database: { name: 'The Keeper', color: '#FF9800', constellation: '💾' },
    tools: { name: 'The Builder', color: '#9C27B0', constellation: '🔧' },
    systems: { name: 'The Architect', color: '#F44336', constellation: '🏗️' }
  }
  
  const patterns: ConstellationPattern[] = []
  
  Object.entries(categories).forEach(([category, info]) => {
    const categorySkills = skills.filter(skill => skill.category === category)
    if (categorySkills.length === 0) return
    
    // Create connections between skills in same category
    const connections: Array<[number, number]> = []
    for (let i = 0; i < categorySkills.length - 1; i++) {
      for (let j = i + 1; j < categorySkills.length; j++) {
        // Connect skills with similar experience levels or direct relationships
        const skill1 = categorySkills[i]
        const skill2 = categorySkills[j]
        
        const experienceDiff = Math.abs(skill1.experience - skill2.experience)
        const levelDiff = Math.abs(skill1.level - skill2.level)
        
        if (experienceDiff < 2 || levelDiff < 0.3 || 
            skill1.connections.includes(skill2.id) || 
            skill2.connections.includes(skill1.id)) {
          connections.push([i, j])
        }
      }
    }
    
    patterns.push({
      name: info.name,
      stars: categorySkills.map(skill => ({
        skill,
        position: skill.position
      })),
      connections,
      color: info.color,
      constellation: info.constellation
    })
  })
  
  return patterns
}

// Individual star component for skills
const SkillStar: React.FC<{
  skill: Skill
  isSelected: boolean
  isHovered: boolean
  onSelect: () => void
  onHover: (hovered: boolean) => void
  intensity: number
}> = ({ skill, isSelected, isHovered, onSelect, onHover, intensity }) => {
  const meshRef = useRef<any>(null!)
  
  const { scale, emissiveIntensity } = useSpring({
    scale: isSelected ? 2 : isHovered ? 1.5 : 1,
    emissiveIntensity: isSelected ? 1 : isHovered ? 0.8 : skill.level * intensity,
    config: { tension: 300, friction: 30 }
  })
  
  // Twinkling effect
  useFrame((state) => {
    if (meshRef.current) {
      const time = state.clock.getElapsedTime()
      const twinkle = Math.sin(time * 3 + skill.level * 10) * 0.1 + 0.9
      meshRef.current.material.opacity = skill.level * twinkle * intensity
    }
  })
  
  const skillColor = useMemo(() => {
    const categories = {
      backend: '#4CAF50',
      frontend: '#2196F3', 
      database: '#FF9800',
      tools: '#9C27B0',
      systems: '#F44336'
    }
    return new Color(categories[skill.category as keyof typeof categories] || '#FFFFFF')
  }, [skill.category])
  
  return (
    <animated.group 
      position={skill.position}
      scale={scale as any}
      onClick={onSelect}
      onPointerOver={() => onHover(true)}
      onPointerOut={() => onHover(false)}
    >
      <Sphere ref={meshRef} args={[0.3, 12, 8]}>
        <meshStandardMaterial
          color={skillColor}
          emissive={skillColor}
          emissiveIntensity={emissiveIntensity as any}
          transparent
          opacity={skill.level * intensity}
        />
      </Sphere>
      
      {/* Skill label */}
      <Text
        position={[0, -1, 0]}
        fontSize={0.4}
        color="white"
        anchorX="center"
        anchorY="middle"
        font="/fonts/Inter-Medium.woff"
        visible={isHovered || isSelected}
      >
        {skill.name}
        <meshStandardMaterial 
          transparent 
          opacity={0.9}
          emissive={skillColor}
          emissiveIntensity={0.2}
        />
      </Text>
      
      {/* Experience indicator */}
      {(isHovered || isSelected) && (
        <Text
          position={[0, -1.8, 0]}
          fontSize={0.25}
          color="#4CAF50"
          anchorX="center"
          anchorY="middle"
          font="/fonts/Inter-Regular.woff"
        >
          {skill.experience}y • {Math.round(skill.level * 100)}%
          <meshStandardMaterial transparent opacity={0.8} />
        </Text>
      )}
      
      {/* Skill level rings */}
      {Array.from({ length: Math.floor(skill.level * 5) }).map((_, index) => (
        <mesh
          key={index}
          position={[0, 0, 0]}
          rotation={[Math.PI / 2, 0, 0]}
        >
          <torusGeometry args={[0.5 + index * 0.2, 0.02, 8, 16]} />
          <meshStandardMaterial
            color={skillColor}
            transparent
            opacity={0.3 - index * 0.05}
            emissive={skillColor}
            emissiveIntensity={0.1}
          />
        </mesh>
      ))}
    </animated.group>
  )
}

// Constellation connection lines
const ConstellationLines: React.FC<{
  pattern: ConstellationPattern
  visible: boolean
  intensity: number
}> = ({ pattern, visible, intensity }) => {
  if (!visible) return null
  
  return (
    <group>
      {pattern.connections.map((connection, index) => {
        const [startIdx, endIdx] = connection
        const start = new Vector3(...pattern.stars[startIdx].position)
        const end = new Vector3(...pattern.stars[endIdx].position)
        
        return (
          <Line
            key={index}
            points={[start, end]}
            color={new Color(pattern.color)}
            transparent
            opacity={intensity * 0.4}
            lineWidth={2}
          />
        )
      })}
    </group>
  )
}

// Main Enhanced Skill Constellation Component
export const EnhancedSkillConstellation: React.FC<EnhancedSkillConstellationProps> = ({
  visible,
  selectedSkill,
  onSkillSelect,
  season,
  timeOfDay
}) => {
  const groupRef = useRef<Group>(null!)
  const [hoveredSkill, setHoveredSkill] = React.useState<Skill | null>(null)
  
  const constellations = useMemo(() => createConstellationPatterns(cameronSkills), [])
  
  // Intensity based on time of day
  const intensity = useMemo(() => {
    switch (timeOfDay) {
      case 'night': return 1
      case 'evening': return 0.8
      case 'dawn': return 0.6
      case 'day': return 0.3
      default: return 0.8
    }
  }, [timeOfDay])
  
  // Gentle rotation of the entire constellation system
  useFrame((state) => {
    if (groupRef.current && visible) {
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.02
      
      // Subtle breathing effect
      const breathe = Math.sin(state.clock.getElapsedTime() * 0.5) * 0.02 + 1
      groupRef.current.scale.setScalar(breathe)
    }
  })
  
  const { opacity } = useSpring({
    opacity: visible ? intensity : 0,
    config: { duration: 2000 }
  })
  
  if (!visible) return null
  
  return (
    <animated.group 
      ref={groupRef} 
      position={[0, 0, 0]}
      opacity={opacity as any}
    >
      {/* Constellation patterns */}
      {constellations.map((pattern, patternIndex) => (
        <group key={pattern.name}>
          {/* Connection lines */}
          <ConstellationLines
            pattern={pattern}
            visible={true}
            intensity={intensity}
          />
          
          {/* Stars */}
          {pattern.stars.map(({ skill }, starIndex) => (
            <SkillStar
              key={skill.id}
              skill={skill}
              isSelected={selectedSkill?.id === skill.id}
              isHovered={hoveredSkill?.id === skill.id}
              onSelect={() => onSkillSelect(skill)}
              onHover={(hovered) => setHoveredSkill(hovered ? skill : null)}
              intensity={intensity}
            />
          ))}
          
          {/* Constellation name label */}
          <Text
            position={[
              pattern.stars.reduce((sum, star) => sum + star.position[0], 0) / pattern.stars.length,
              pattern.stars.reduce((sum, star) => sum + star.position[1], 0) / pattern.stars.length + 5,
              pattern.stars.reduce((sum, star) => sum + star.position[2], 0) / pattern.stars.length
            ]}
            fontSize={0.6}
            color={pattern.color}
            anchorX="center"
            anchorY="middle"
            font="/fonts/Inter-Bold.woff"
            visible={intensity > 0.7}
          >
            {pattern.constellation} {pattern.name}
            <meshStandardMaterial 
              transparent 
              opacity={intensity * 0.8}
              emissive={new Color(pattern.color)}
              emissiveIntensity={0.3}
            />
          </Text>
        </group>
      ))}
      
      {/* Central connecting hub - represents Cameron as the developer */}
      <Sphere args={[1, 16, 12]} position={[0, 45, -35]}>
        <meshStandardMaterial
          color="#FFFFFF"
          emissive="#FFFFFF" 
          emissiveIntensity={intensity * 0.5}
          transparent
          opacity={intensity * 0.3}
        />
      </Sphere>
      
      <Text
        position={[0, 42, -35]}
        fontSize={0.5}
        color="white"
        anchorX="center"
        anchorY="middle"
        font="/fonts/Inter-Bold.woff"
        visible={intensity > 0.5}
      >
        Cameron Potter
        <meshStandardMaterial 
          transparent 
          opacity={intensity}
          emissive="#FFFFFF"
          emissiveIntensity={0.3}
        />
      </Text>
      
      <Text
        position={[0, 40.5, -35]}
        fontSize={0.3}
        color="#4CAF50"
        anchorX="center"
        anchorY="middle"
        font="/fonts/Inter-Medium.woff"
        visible={intensity > 0.5}
      >
        Full-Stack Developer
        <meshStandardMaterial 
          transparent 
          opacity={intensity * 0.8}
        />
      </Text>
    </animated.group>
  )
}