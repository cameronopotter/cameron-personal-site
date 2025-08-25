import React, { useState, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Text, Html, RoundedBox, Sphere } from '@react-three/drei'
import { 
  Box, 
  Typography, 
  Button, 
  Card, 
  CardContent, 
  Grid, 
  Chip, 
  LinearProgress,
  Avatar,
  Link
} from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'
import { useSpring, animated } from '@react-spring/three'
import { Group, Vector3, Color } from 'three'
import { GitHub, Email, Phone, School, Work, LocationOn } from '@mui/icons-material'

interface AboutCameronProps {
  position: [number, number, number]
  visible: boolean
  onClose: () => void
}

// Cameron's professional data based on resume
const cameronData = {
  name: "Cameron Potter",
  title: "Full-Stack Software Engineer",
  email: "cameronopotter@gmail.com", 
  phone: "8036036393",
  location: "Columbia, SC",
  github: "https://github.com/cameronopotter",
  
  summary: "Passionate full-stack developer with expertise in modern web technologies. Currently pursuing Computer Science degree while working as a Software Engineer at Louddoor, building scalable web applications with PHP, Laravel, Vue.js, and modern development practices.",
  
  experience: [
    {
      title: "Software Engineer",
      company: "Louddoor",
      period: "Current",
      description: "Full-stack development using PHP, Laravel, Vue.js, and Agile methodologies. Building scalable web applications and maintaining high-quality code standards.",
      technologies: ["PHP", "Laravel", "Vue.js", "MySQL", "Agile"]
    },
    {
      title: "Previous Experience",
      company: "Benty, Griffin Pools & Spas",
      period: "Previous Roles",
      description: "Gained valuable development experience across multiple organizations, building expertise in various technologies and business domains.",
      technologies: ["Web Development", "Database Design", "Client Relations"]
    }
  ],
  
  education: {
    degree: "Bachelor of Science in Computer Science",
    school: "Western Governors University",
    expectedGraduation: "August 2025",
    status: "In Progress"
  },
  
  skills: {
    languages: [
      { name: "PHP", level: 90, color: "#777BB4" },
      { name: "JavaScript", level: 85, color: "#F7DF1E" },
      { name: "Python", level: 80, color: "#3776AB" },
      { name: "Java", level: 70, color: "#007396" },
      { name: "C++", level: 65, color: "#00599C" },
      { name: "C#", level: 60, color: "#239120" }
    ],
    frameworks: [
      { name: "Laravel", level: 90, color: "#FF2D20" },
      { name: "Vue.js", level: 85, color: "#4FC08D" },
      { name: "React", level: 80, color: "#61DAFB" },
      { name: "Node.js", level: 75, color: "#339933" }
    ],
    tools: [
      { name: "Git", level: 85, color: "#F05032" },
      { name: "MySQL", level: 80, color: "#4479A1" },
      { name: "Docker", level: 70, color: "#2496ED" },
      { name: "AWS", level: 65, color: "#232F3E" }
    ]
  }
}

// 3D Interactive About Panel
const About3DPanel: React.FC<{
  position: [number, number, number]
  visible: boolean
  onInteract: (section: string) => void
}> = ({ position, visible, onInteract }) => {
  const groupRef = useRef<Group>(null!)
  const [hoveredSection, setHoveredSection] = useState<string | null>(null)

  useFrame((state) => {
    if (groupRef.current && visible) {
      groupRef.current.rotation.y = Math.sin(state.clock.getElapsedTime() * 0.5) * 0.1
    }
  })

  const { scale } = useSpring({
    scale: visible ? 1 : 0,
    config: { tension: 300, friction: 30 }
  })

  if (!visible) return null

  return (
    <animated.group ref={groupRef} position={position} scale={scale as any}>
      {/* Main info sphere */}
      <Sphere
        args={[2, 32, 32]}
        position={[0, 0, 0]}
        onClick={() => onInteract('profile')}
        onPointerOver={() => setHoveredSection('profile')}
        onPointerOut={() => setHoveredSection(null)}
      >
        <meshStandardMaterial
          color={hoveredSection === 'profile' ? '#4CAF50' : '#2196F3'}
          emissive={hoveredSection === 'profile' ? '#1B5E20' : '#0D47A1'}
          emissiveIntensity={0.3}
          transparent
          opacity={0.8}
        />
      </Sphere>

      {/* Floating skill orbs */}
      {cameronData.skills.languages.slice(0, 4).map((skill, index) => {
        const angle = (index / 4) * Math.PI * 2
        const radius = 4
        const x = Math.cos(angle) * radius
        const z = Math.sin(angle) * radius

        return (
          <Sphere
            key={skill.name}
            args={[0.5, 16, 16]}
            position={[x, Math.sin(angle * 2) * 0.5, z]}
            onClick={() => onInteract('skills')}
            onPointerOver={() => setHoveredSection(skill.name)}
            onPointerOut={() => setHoveredSection(null)}
          >
            <meshStandardMaterial
              color={skill.color}
              emissive={skill.color}
              emissiveIntensity={hoveredSection === skill.name ? 0.5 : 0.2}
              transparent
              opacity={0.9}
            />
          </Sphere>
        )
      })}

      {/* Main label */}
      <Text
        position={[0, -3, 0]}
        fontSize={0.5}
        color="white"
        anchorX="center"
        anchorY="middle"
        font="/fonts/Inter-Bold.woff"
      >
        About Cameron
        <meshStandardMaterial transparent opacity={0.9} />
      </Text>

      {/* Interactive hints */}
      <Text
        position={[0, -4, 0]}
        fontSize={0.2}
        color="#4CAF50"
        anchorX="center"
        anchorY="middle"
        font="/fonts/Inter-Medium.woff"
      >
        Click to explore
        <meshStandardMaterial transparent opacity={0.7} />
      </Text>
    </animated.group>
  )
}

// Main About Cameron Component
export const AboutCameron: React.FC<AboutCameronProps> = ({ 
  position, 
  visible, 
  onClose 
}) => {
  const [activeSection, setActiveSection] = useState<string | null>(null)

  const handleInteract = (section: string) => {
    setActiveSection(section)
  }

  return (
    <group>
      {/* 3D Interactive Element */}
      <About3DPanel 
        position={position}
        visible={visible && !activeSection}
        onInteract={handleInteract}
      />

      {/* HTML Overlay for detailed information */}
      {activeSection && (
        <Html
          position={[position[0], position[1], position[2]]}
          transform
          occlude
          center
        >
          <Box
            sx={{
              width: '800px',
              maxHeight: '600px',
              bgcolor: 'rgba(26, 26, 26, 0.95)',
              backdropFilter: 'blur(20px)',
              borderRadius: 4,
              p: 4,
              border: '1px solid rgba(76, 175, 80, 0.3)',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.8)',
              overflow: 'auto'
            }}
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={activeSection}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Avatar
                    sx={{ 
                      width: 80, 
                      height: 80, 
                      mr: 3,
                      bgcolor: '#4CAF50',
                      fontSize: '2rem',
                      fontWeight: 'bold'
                    }}
                  >
                    CP
                  </Avatar>
                  <Box>
                    <Typography variant="h3" color="white" fontWeight="bold">
                      {cameronData.name}
                    </Typography>
                    <Typography variant="h6" color="#4CAF50" mb={1}>
                      {cameronData.title}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                      <Chip 
                        icon={<LocationOn />} 
                        label={cameronData.location} 
                        size="small" 
                        variant="outlined"
                        sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}
                      />
                      <Chip 
                        icon={<Email />} 
                        label={cameronData.email} 
                        size="small" 
                        variant="outlined"
                        sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}
                        onClick={() => window.open(`mailto:${cameronData.email}`)}
                      />
                      <Chip 
                        icon={<Phone />} 
                        label={cameronData.phone} 
                        size="small" 
                        variant="outlined"
                        sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}
                        onClick={() => window.open(`tel:${cameronData.phone}`)}
                      />
                    </Box>
                  </Box>
                </Box>

                {/* Professional Summary */}
                {activeSection === 'profile' && (
                  <>
                    <Typography variant="h5" color="#4CAF50" mb={2}>
                      Professional Summary
                    </Typography>
                    <Typography variant="body1" color="white" mb={3} lineHeight={1.6}>
                      {cameronData.summary}
                    </Typography>

                    {/* Current Experience */}
                    <Typography variant="h5" color="#4CAF50" mb={2}>
                      Current Role
                    </Typography>
                    <Card sx={{ mb: 3, bgcolor: 'rgba(255,255,255,0.05)' }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Work sx={{ color: '#4CAF50', mr: 1 }} />
                          <Typography variant="h6" color="white">
                            {cameronData.experience[0].title} at {cameronData.experience[0].company}
                          </Typography>
                        </Box>
                        <Typography variant="body2" color="rgba(255,255,255,0.7)" mb={2}>
                          {cameronData.experience[0].description}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          {cameronData.experience[0].technologies.map((tech) => (
                            <Chip 
                              key={tech} 
                              label={tech} 
                              size="small" 
                              sx={{ bgcolor: 'rgba(76, 175, 80, 0.2)', color: '#4CAF50' }}
                            />
                          ))}
                        </Box>
                      </CardContent>
                    </Card>

                    {/* Education */}
                    <Typography variant="h5" color="#4CAF50" mb={2}>
                      Education
                    </Typography>
                    <Card sx={{ mb: 3, bgcolor: 'rgba(255,255,255,0.05)' }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <School sx={{ color: '#4CAF50', mr: 1 }} />
                          <Box>
                            <Typography variant="h6" color="white">
                              {cameronData.education.degree}
                            </Typography>
                            <Typography variant="body2" color="rgba(255,255,255,0.7)">
                              {cameronData.education.school} • Expected {cameronData.education.expectedGraduation}
                            </Typography>
                          </Box>
                        </Box>
                        <Chip 
                          label={`Status: ${cameronData.education.status}`}
                          size="small" 
                          sx={{ bgcolor: 'rgba(33, 150, 243, 0.2)', color: '#2196F3' }}
                        />
                      </CardContent>
                    </Card>
                  </>
                )}

                {/* Skills Section */}
                {activeSection === 'skills' && (
                  <>
                    <Typography variant="h5" color="#4CAF50" mb={3}>
                      Technical Skills
                    </Typography>
                    
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={4}>
                        <Typography variant="h6" color="white" mb={2}>Languages</Typography>
                        {cameronData.skills.languages.map((skill) => (
                          <Box key={skill.name} sx={{ mb: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                              <Typography variant="body2" color="white">{skill.name}</Typography>
                              <Typography variant="body2" color="rgba(255,255,255,0.7)">
                                {skill.level}%
                              </Typography>
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={skill.level}
                              sx={{
                                bgcolor: 'rgba(255,255,255,0.1)',
                                '& .MuiLinearProgress-bar': { bgcolor: skill.color }
                              }}
                            />
                          </Box>
                        ))}
                      </Grid>
                      
                      <Grid item xs={12} md={4}>
                        <Typography variant="h6" color="white" mb={2}>Frameworks</Typography>
                        {cameronData.skills.frameworks.map((skill) => (
                          <Box key={skill.name} sx={{ mb: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                              <Typography variant="body2" color="white">{skill.name}</Typography>
                              <Typography variant="body2" color="rgba(255,255,255,0.7)">
                                {skill.level}%
                              </Typography>
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={skill.level}
                              sx={{
                                bgcolor: 'rgba(255,255,255,0.1)',
                                '& .MuiLinearProgress-bar': { bgcolor: skill.color }
                              }}
                            />
                          </Box>
                        ))}
                      </Grid>
                      
                      <Grid item xs={12} md={4}>
                        <Typography variant="h6" color="white" mb={2}>Tools & Platforms</Typography>
                        {cameronData.skills.tools.map((skill) => (
                          <Box key={skill.name} sx={{ mb: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                              <Typography variant="body2" color="white">{skill.name}</Typography>
                              <Typography variant="body2" color="rgba(255,255,255,0.7)">
                                {skill.level}%
                              </Typography>
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={skill.level}
                              sx={{
                                bgcolor: 'rgba(255,255,255,0.1)',
                                '& .MuiLinearProgress-bar': { bgcolor: skill.color }
                              }}
                            />
                          </Box>
                        ))}
                      </Grid>
                    </Grid>
                  </>
                )}

                {/* Action Buttons */}
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 4 }}>
                  <Button
                    variant="contained"
                    startIcon={<GitHub />}
                    onClick={() => window.open(cameronData.github, '_blank')}
                    sx={{ bgcolor: '#4CAF50', '&:hover': { bgcolor: '#45a049' } }}
                  >
                    View GitHub
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() => setActiveSection(activeSection === 'profile' ? 'skills' : 'profile')}
                    sx={{ borderColor: '#4CAF50', color: '#4CAF50' }}
                  >
                    {activeSection === 'profile' ? 'View Skills' : 'View Profile'}
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={onClose}
                    sx={{ borderColor: 'rgba(255,255,255,0.3)', color: 'white' }}
                  >
                    Back to Garden
                  </Button>
                </Box>
              </motion.div>
            </AnimatePresence>
          </Box>
        </Html>
      )}
    </group>
  )
}