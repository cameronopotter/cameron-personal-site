import React, { useRef, useMemo, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Text, Html, RoundedBox, Sphere } from '@react-three/drei'
import { Group, Vector3, Color } from 'three'
import { useSpring, animated } from '@react-spring/three'
import { Box, Typography, Chip, Avatar } from '@mui/material'
import { GitHub, LinkedIn, Email, School, Work, Code } from '@mui/icons-material'

interface FloatingInfoPanelsProps {
  visible?: boolean
  complexity?: number
}

// Cameron's resume data
const cameronInfo = {
  name: "Cameron Potter",
  title: "Full-Stack Software Engineer",
  email: "cameronopotter@gmail.com",
  location: "Columbia, SC",
  github: "https://github.com/cameronopotter",
  
  currentRole: {
    title: "Software Engineer",
    company: "Louddoor",
    technologies: ["PHP", "Laravel", "Vue.js", "MySQL"],
    description: "Building scalable web applications with modern technologies"
  },
  
  education: {
    degree: "Bachelor of Science in Computer Science",
    school: "Western Governors University",
    status: "In Progress - Expected Aug 2025"
  },
  
  topSkills: [
    { name: "PHP", level: 90, color: "#777BB4" },
    { name: "Laravel", level: 90, color: "#FF2D20" },
    { name: "JavaScript", level: 85, color: "#F7DF1E" },
    { name: "Vue.js", level: 85, color: "#4FC08D" },
    { name: "Python", level: 80, color: "#3776AB" },
    { name: "React", level: 80, color: "#61DAFB" },
  ]
}

// Floating Professional Info Panel
const ProfessionalInfoPanel: React.FC<{
  position: [number, number, number]
  visible: boolean
}> = ({ position, visible }) => {
  const panelRef = useRef<Group>(null!)
  const [isHovered, setIsHovered] = useState(false)
  
  useFrame((state) => {
    if (panelRef.current && visible) {
      const time = state.clock.getElapsedTime()
      // Gentle floating animation
      panelRef.current.position.y = position[1] + Math.sin(time * 0.8) * 0.1
      panelRef.current.rotation.y = Math.sin(time * 0.3) * 0.05
    }
  })
  
  const { scale } = useSpring({
    scale: visible ? (isHovered ? 1.1 : 1) : 0,
    config: { tension: 300, friction: 30 }
  })
  
  return (
    <animated.group 
      ref={panelRef} 
      position={position}
      scale={scale as any}
      onPointerOver={() => setIsHovered(true)}
      onPointerOut={() => setIsHovered(false)}
    >
      {/* Panel Background */}
      <RoundedBox
        args={[4, 2.5, 0.1]}
        radius={0.1}
      >
        <meshStandardMaterial
          color="#000022"
          emissive="#001133"
          emissiveIntensity={0.3}
          transparent
          opacity={0.9}
          metalness={0.3}
          roughness={0.2}
        />
      </RoundedBox>
      
      {/* Neon Border */}
      <RoundedBox
        args={[4.1, 2.6, 0.05]}
        position={[0, 0, 0.05]}
        radius={0.1}
      >
        <meshStandardMaterial
          color="#00FFFF"
          emissive="#00FFFF"
          emissiveIntensity={0.6}
          transparent
          opacity={0.4}
        />
      </RoundedBox>
      
      {/* Content */}
      <Html
        position={[0, 0, 0.11]}
        transform
        occlude
        center
        distanceFactor={6}
      >
        <Box
          sx={{
            width: '400px',
            height: '250px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            p: 2,
            color: 'white'
          }}
        >
          <Avatar
            sx={{ 
              width: 60, 
              height: 60, 
              mb: 2,
              bgcolor: '#00FFFF',
              fontSize: '1.5rem',
              fontWeight: 'bold'
            }}
          >
            CP
          </Avatar>
          
          <Typography variant="h5" fontWeight="bold" sx={{ mb: 1 }}>
            {cameronInfo.name}
          </Typography>
          
          <Typography variant="subtitle1" sx={{ color: '#00FFFF', mb: 2 }}>
            {cameronInfo.title}
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
            <Chip
              icon={<Work sx={{ color: '#4CAF50' }} />}
              label={`${cameronInfo.currentRole.title} @ ${cameronInfo.currentRole.company}`}
              size="small"
              sx={{ bgcolor: 'rgba(76, 175, 80, 0.2)', color: '#4CAF50', fontSize: '0.7rem' }}
            />
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
            <Chip
              icon={<School />}
              label="WGU Computer Science"
              size="small"
              sx={{ bgcolor: 'rgba(33, 150, 243, 0.2)', color: '#2196F3', fontSize: '0.6rem' }}
            />
            <Chip
              label={cameronInfo.location}
              size="small"
              sx={{ bgcolor: 'rgba(255, 152, 0, 0.2)', color: '#FF9800', fontSize: '0.6rem' }}
            />
          </Box>
        </Box>
      </Html>
      
      {/* Connecting Lines to Projects */}
      <mesh position={[0, -1.5, 0]}>
        <cylinderGeometry args={[0.02, 0.02, 1, 8]} />
        <meshStandardMaterial
          color="#00FFFF"
          emissive="#00FFFF"
          emissiveIntensity={0.5}
          transparent
          opacity={0.6}
        />
      </mesh>
    </animated.group>
  )
}

// Skills Showcase Panel
const SkillsPanel: React.FC<{
  position: [number, number, number]
  visible: boolean
}> = ({ position, visible }) => {
  const panelRef = useRef<Group>(null!)
  
  useFrame((state) => {
    if (panelRef.current && visible) {
      const time = state.clock.getElapsedTime()
      panelRef.current.position.y = position[1] + Math.sin(time * 1.2 + Math.PI) * 0.08
      panelRef.current.rotation.y = Math.cos(time * 0.4) * 0.03
    }
  })
  
  const { scale } = useSpring({
    scale: visible ? 1 : 0,
    config: { tension: 300, friction: 30 }
  })
  
  return (
    <animated.group ref={panelRef} position={position} scale={scale as any}>
      {/* Panel Background */}
      <RoundedBox args={[3.5, 3, 0.1]} radius={0.1}>
        <meshStandardMaterial
          color="#002200"
          emissive="#001100"
          emissiveIntensity={0.3}
          transparent
          opacity={0.9}
        />
      </RoundedBox>
      
      {/* Skills Content */}
      <Html
        position={[0, 0, 0.11]}
        transform
        occlude
        center
        distanceFactor={7}
      >
        <Box sx={{ width: '350px', p: 2, color: 'white', textAlign: 'center' }}>
          <Typography variant="h6" sx={{ mb: 2, color: '#00FF00' }}>
            <Code sx={{ mr: 1 }} />
            Technical Skills
          </Typography>
          
          {cameronInfo.topSkills.slice(0, 6).map((skill, index) => (
            <Box key={skill.name} sx={{ mb: 1, textAlign: 'left' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="caption" color="white" fontSize="0.7rem">
                  {skill.name}
                </Typography>
                <Typography variant="caption" color="rgba(255,255,255,0.7)" fontSize="0.6rem">
                  {skill.level}%
                </Typography>
              </Box>
              <Box
                sx={{
                  width: '100%',
                  height: 4,
                  bgcolor: 'rgba(255,255,255,0.1)',
                  borderRadius: 1,
                  position: 'relative'
                }}
              >
                <Box
                  sx={{
                    width: `${skill.level}%`,
                    height: '100%',
                    bgcolor: skill.color,
                    borderRadius: 1,
                    boxShadow: `0 0 8px ${skill.color}50`
                  }}
                />
              </Box>
            </Box>
          ))}
        </Box>
      </Html>
      
      {/* Orbiting skill icons */}
      {cameronInfo.topSkills.slice(0, 4).map((skill, index) => {
        const angle = (index / 4) * Math.PI * 2
        const radius = 2.2
        
        return (
          <Sphere
            key={skill.name}
            args={[0.15, 12, 8]}
            position={[
              Math.cos(angle) * radius,
              Math.sin(angle) * 0.5,
              Math.sin(angle) * radius * 0.3
            ]}
          >
            <meshStandardMaterial
              color={skill.color}
              emissive={skill.color}
              emissiveIntensity={0.4}
              transparent
              opacity={0.8}
            />
          </Sphere>
        )
      })}
    </animated.group>
  )
}

// Contact Info Panel  
const ContactPanel: React.FC<{
  position: [number, number, number]
  visible: boolean
}> = ({ position, visible }) => {
  const panelRef = useRef<Group>(null!)
  
  useFrame((state) => {
    if (panelRef.current && visible) {
      const time = state.clock.getElapsedTime()
      panelRef.current.position.y = position[1] + Math.sin(time * 0.6 + Math.PI/3) * 0.12
    }
  })
  
  return (
    <animated.group ref={panelRef} position={position}>
      <RoundedBox args={[2.5, 1.5, 0.1]} radius={0.1}>
        <meshStandardMaterial
          color="#220022"
          emissive="#110011"
          emissiveIntensity={0.3}
          transparent
          opacity={0.9}
        />
      </RoundedBox>
      
      <Html
        position={[0, 0, 0.11]}
        transform
        occlude
        center
        distanceFactor={8}
      >
        <Box sx={{ width: '250px', p: 2, color: 'white', textAlign: 'center' }}>
          <Typography variant="h6" sx={{ mb: 2, color: '#FF1493' }}>
            Let's Connect
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Chip
              icon={<GitHub />}
              label="GitHub"
              size="small"
              clickable
              onClick={() => window.open('https://github.com/cameronopotter', '_blank')}
              sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)', color: 'white', '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.2)' } }}
            />
            <Chip
              icon={<Email />}
              label="Email Me"
              size="small"
              clickable
              onClick={() => window.open(`mailto:${cameronInfo.email}`, '_blank')}
              sx={{ bgcolor: 'rgba(255, 20, 147, 0.2)', color: '#FF1493' }}
            />
          </Box>
        </Box>
      </Html>
    </animated.group>
  )
}

// Main Component
export const FloatingInfoPanels: React.FC<FloatingInfoPanelsProps> = ({
  visible = true,
  complexity = 3
}) => {
  if (!visible || complexity < 2) return null
  
  return (
    <group>
      {/* Professional Info - Central position */}
      <ProfessionalInfoPanel
        position={[0, 4, -8]}
        visible={visible}
      />
      
      {/* Skills Panel - Right side */}
      {complexity > 2 && (
        <SkillsPanel
          position={[12, 3, -5]}
          visible={visible}
        />
      )}
      
      {/* Contact Panel - Left side */}
      {complexity > 1 && (
        <ContactPanel
          position={[-10, 3.5, -3]}
          visible={visible}
        />
      )}
    </group>
  )
}