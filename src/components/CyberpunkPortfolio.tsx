import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Box, Typography, IconButton, Drawer, Avatar } from '@mui/material'
import { Menu, Close, GitHub, Work, Person, Code } from '@mui/icons-material'
import { Canvas, useFrame } from '@react-three/fiber'
import { Sphere, Box as ThreeBox } from '@react-three/drei'
import { Vector3, Color } from 'three'

// Optimized Rain Particles Component
const CyberpunkRain: React.FC = () => {
  const rainRef = useRef<any>(null)
  const particlesCount = 200 // Reduced for performance
  
  const particles = React.useMemo(() => {
    const positions = new Float32Array(particlesCount * 3)
    const speeds = new Float32Array(particlesCount)
    
    for (let i = 0; i < particlesCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 20
      positions[i * 3 + 1] = Math.random() * 20 + 10
      positions[i * 3 + 2] = (Math.random() - 0.5) * 20
      speeds[i] = Math.random() * 0.02 + 0.01
    }
    
    return { positions, speeds }
  }, [])
  
  useFrame(() => {
    if (!rainRef.current) return
    
    const positions = rainRef.current.geometry.attributes.position.array
    
    for (let i = 0; i < particlesCount; i++) {
      positions[i * 3 + 1] -= particles.speeds[i]
      
      if (positions[i * 3 + 1] < -5) {
        positions[i * 3 + 1] = 15
        positions[i * 3] = (Math.random() - 0.5) * 20
        positions[i * 3 + 2] = (Math.random() - 0.5) * 20
      }
    }
    
    rainRef.current.geometry.attributes.position.needsUpdate = true
  })
  
  return (
    <points ref={rainRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          array={particles.positions}
          count={particlesCount}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        color="#00ffff"
        size={0.1}
        transparent
        opacity={0.6}
      />
    </points>
  )
}

// Cyberpunk Grid Background
const CyberpunkGrid: React.FC = () => {
  return (
    <group>
      {/* Ground Grid */}
      {Array.from({ length: 21 }).map((_, i) => (
        <ThreeBox
          key={`grid-x-${i}`}
          args={[20, 0.01, 0.05]}
          position={[0, -5, -10 + i]}
        >
          <meshBasicMaterial color="#00ffff" transparent opacity={0.2} />
        </ThreeBox>
      ))}
      {Array.from({ length: 21 }).map((_, i) => (
        <ThreeBox
          key={`grid-z-${i}`}
          args={[0.05, 0.01, 20]}
          position={[-10 + i, -5, 0]}
        >
          <meshBasicMaterial color="#00ffff" transparent opacity={0.2} />
        </ThreeBox>
      ))}
    </group>
  )
}

// Simple 3D Scene - Optimized
const CyberpunkScene: React.FC = () => {
  return (
    <>
      <ambientLight intensity={0.3} color="#001133" />
      <directionalLight position={[10, 10, 5]} intensity={1} color="#00ffff" />
      <CyberpunkGrid />
      <CyberpunkRain />
      
      {/* Floating Orbs */}
      <Sphere args={[1, 16, 16]} position={[-3, 2, -5]}>
        <meshStandardMaterial
          color="#00ffff"
          emissive="#00ffff"
          emissiveIntensity={0.3}
          transparent
          opacity={0.7}
        />
      </Sphere>
      
      <Sphere args={[0.8, 16, 16]} position={[4, 1, -3]}>
        <meshStandardMaterial
          color="#ff00ff"
          emissive="#ff00ff"
          emissiveIntensity={0.3}
          transparent
          opacity={0.7}
        />
      </Sphere>
    </>
  )
}

// Navigation Menu
const NavigationMenu: React.FC<{ 
  isOpen: boolean
  onClose: () => void
  activeSection: string
  setActiveSection: (section: string) => void
}> = ({ isOpen, onClose, activeSection, setActiveSection }) => {
  const menuItems = [
    { id: 'about', label: 'About Me', icon: <Person /> },
    { id: 'projects', label: 'Projects', icon: <Code /> },
    { id: 'experience', label: 'Experience', icon: <Work /> },
    { id: 'github', label: 'GitHub Activity', icon: <GitHub /> }
  ]
  
  return (
    <Drawer
      anchor="right"
      open={isOpen}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: 300,
          background: 'linear-gradient(135deg, rgba(0,0,20,0.95), rgba(0,20,40,0.95))',
          backdropFilter: 'blur(20px)',
          border: '1px solid #00ffff',
          borderRight: 'none'
        }
      }}
    >
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h6" sx={{ color: '#00ffff', fontWeight: 700 }}>
            NAVIGATION
          </Typography>
          <IconButton onClick={onClose} sx={{ color: '#00ffff' }}>
            <Close />
          </IconButton>
        </Box>
        
        {menuItems.map((item) => (
          <motion.div
            key={item.id}
            whileHover={{ x: 10 }}
            whileTap={{ scale: 0.98 }}
          >
            <Box
              onClick={() => {
                setActiveSection(item.id)
                onClose()
              }}
              sx={{
                display: 'flex',
                alignItems: 'center',
                p: 2,
                mb: 1,
                cursor: 'pointer',
                borderRadius: 1,
                border: '1px solid transparent',
                background: activeSection === item.id ? 'rgba(0,255,255,0.1)' : 'transparent',
                borderColor: activeSection === item.id ? '#00ffff' : 'transparent',
                '&:hover': {
                  background: 'rgba(0,255,255,0.05)',
                  borderColor: '#00ffff'
                }
              }}
            >
              <Box sx={{ color: '#00ffff', mr: 2 }}>
                {item.icon}
              </Box>
              <Typography sx={{ color: 'white', fontWeight: 500 }}>
                {item.label}
              </Typography>
            </Box>
          </motion.div>
        ))}
      </Box>
    </Drawer>
  )
}

// Content Sections
const AboutSection: React.FC = () => (
  <Box sx={{ maxWidth: 800 }}>
    <Typography variant="h3" sx={{ color: '#00ffff', mb: 3, fontWeight: 700 }}>
      Cameron Potter
    </Typography>
    <Typography variant="h5" sx={{ color: '#ff00ff', mb: 4, fontWeight: 400 }}>
      Full-Stack Software Engineer
    </Typography>
    <Typography sx={{ color: 'white', fontSize: '1.1rem', lineHeight: 1.8, mb: 4 }}>
      Passionate software engineer at Louddoor, building scalable web applications with modern technologies. 
      Currently pursuing Computer Science at Western Governors University.
    </Typography>
    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
      {['PHP', 'Laravel', 'Vue.js', 'JavaScript', 'Python', 'React', 'MySQL'].map((tech) => (
        <Box
          key={tech}
          sx={{
            px: 2,
            py: 1,
            border: '1px solid #00ffff',
            borderRadius: 1,
            color: '#00ffff',
            fontSize: '0.9rem',
            background: 'rgba(0,255,255,0.1)'
          }}
        >
          {tech}
        </Box>
      ))}
    </Box>
  </Box>
)

const ProjectsSection: React.FC = () => (
  <Box>
    <Typography variant="h4" sx={{ color: '#00ffff', mb: 4, fontWeight: 700 }}>
      Featured Projects
    </Typography>
    <Box sx={{ display: 'grid', gap: 3, gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
      {[
        { name: 'Digital Greenhouse', tech: 'React, Three.js, TypeScript', desc: 'Interactive 3D portfolio showcasing projects and skills' },
        { name: 'E-commerce Platform', tech: 'Laravel, Vue.js, MySQL', desc: 'Full-stack e-commerce solution with modern UI' },
        { name: 'Task Management System', tech: 'Python, FastAPI, PostgreSQL', desc: 'Collaborative project management tool' }
      ].map((project) => (
        <motion.div
          key={project.name}
          whileHover={{ scale: 1.02, y: -5 }}
          transition={{ duration: 0.2 }}
        >
          <Box
            sx={{
              p: 3,
              border: '1px solid #00ffff',
              borderRadius: 2,
              background: 'rgba(0,255,255,0.05)',
              backdropFilter: 'blur(10px)'
            }}
          >
            <Typography variant="h6" sx={{ color: '#00ffff', mb: 2 }}>
              {project.name}
            </Typography>
            <Typography sx={{ color: '#ff00ff', fontSize: '0.9rem', mb: 2 }}>
              {project.tech}
            </Typography>
            <Typography sx={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.9rem' }}>
              {project.desc}
            </Typography>
          </Box>
        </motion.div>
      ))}
    </Box>
  </Box>
)

// GitHub Activity Section
const GitHubSection: React.FC = () => (
  <Box>
    <Typography variant="h4" sx={{ color: '#00ffff', mb: 4, fontWeight: 700 }}>
      GitHub Activity
    </Typography>
    <Box sx={{ 
      p: 3, 
      border: '1px solid #00ffff', 
      borderRadius: 2, 
      background: 'rgba(0,255,255,0.05)',
      backdropFilter: 'blur(10px)'
    }}>
      <Typography sx={{ color: 'white', mb: 3 }}>
        Follow my development journey on GitHub where I contribute to open source projects 
        and build innovative solutions.
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 3 }}>
        {['React', 'TypeScript', 'Python', 'JavaScript', 'Laravel', 'Vue.js'].map((lang) => (
          <Box
            key={lang}
            sx={{
              px: 2,
              py: 1,
              border: '1px solid #ff00ff',
              borderRadius: 1,
              color: '#ff00ff',
              fontSize: '0.8rem',
              background: 'rgba(255,0,255,0.1)'
            }}
          >
            {lang}
          </Box>
        ))}
      </Box>
      <Typography sx={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.9rem' }}>
        📊 Recent contributions include full-stack applications, 3D visualizations, and developer tools.
      </Typography>
    </Box>
  </Box>
)

// Experience Section - Career Timeline
const ExperienceSection: React.FC = () => (
  <Box>
    <Typography variant="h4" sx={{ color: '#00ffff', mb: 4, fontWeight: 700 }}>
      Career Timeline
    </Typography>
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* PlantSitter Labs - Current */}
      <Box sx={{
        p: 3,
        border: '1px solid #00ffff',
        borderRadius: 2,
        background: 'rgba(0,255,255,0.05)',
        backdropFilter: 'blur(10px)',
        position: 'relative'
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ color: '#00ffff', mb: 1 }}>
              Senior Developer
            </Typography>
            <Typography sx={{ color: '#ff00ff', mb: 1 }}>
              PlantSitter Labs • Columbia, SC
            </Typography>
          </Box>
          <Typography sx={{ color: '#00ffff', fontSize: '0.9rem', fontWeight: 600 }}>
            05/2025 - Current
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
          {['AWS', 'Tailwind CSS', 'Agile'].map((tech) => (
            <Box
              key={tech}
              sx={{
                px: 2,
                py: 0.5,
                border: '1px solid #00ffff',
                borderRadius: 1,
                color: '#00ffff',
                fontSize: '0.8rem',
                background: 'rgba(0,255,255,0.1)'
              }}
            >
              {tech}
            </Box>
          ))}
        </Box>
        <Typography sx={{ color: 'rgba(255,255,255,0.8)', lineHeight: 1.6, fontSize: '0.95rem' }}>
          • Developed responsive web applications using HTML, CSS, and JavaScript frameworks.<br/>
          • Implemented database solutions using MySQL and MongoDB for data management.<br/>
          • Built RESTful web services using the Laravel Framework and JSON data formats.<br/>
          • Configured and maintained cloud-based data infrastructure on platforms like AWS, Azure, and Google Cloud to enhance data storage and computation capabilities.<br/>
          • Supported the testing and validation of AI applications in real-world scenarios.
        </Typography>
      </Box>

      {/* Louddoor Software Engineer */}
      <Box sx={{
        p: 3,
        border: '1px solid #00ffff',
        borderRadius: 2,
        background: 'rgba(0,255,255,0.05)',
        backdropFilter: 'blur(10px)'
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ color: '#00ffff', mb: 1 }}>
              Software Engineer
            </Typography>
            <Typography sx={{ color: '#ff00ff', mb: 1 }}>
              Louddoor • Columbia, SC
            </Typography>
          </Box>
          <Typography sx={{ color: '#00ffff', fontSize: '0.9rem', fontWeight: 600 }}>
            06/2023 - Current
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
          {['PHP', 'Laravel', 'Agile', 'Team Collaboration'].map((tech) => (
            <Box
              key={tech}
              sx={{
                px: 2,
                py: 0.5,
                border: '1px solid #00ffff',
                borderRadius: 1,
                color: '#00ffff',
                fontSize: '0.8rem',
                background: 'rgba(0,255,255,0.1)'
              }}
            >
              {tech}
            </Box>
          ))}
        </Box>
        <Typography sx={{ color: 'rgba(255,255,255,0.8)', lineHeight: 1.6, fontSize: '0.95rem' }}>
          • Developed and tested software applications with modern programming languages.<br/>
          • Collaborated with team members to gather project requirements efficiently.<br/>
          • Assisted in troubleshooting and debugging of existing software systems.<br/>
          • Documented design and development processes for future reference.<br/>
          • Participated in code reviews to uphold quality standards.<br/>
          • Utilized PHP frameworks, including Laravel, to enhance application scalability.
        </Typography>
      </Box>

      {/* Louddoor Intern */}
      <Box sx={{
        p: 3,
        border: '1px solid #666',
        borderRadius: 2,
        background: 'rgba(102,102,102,0.05)',
        backdropFilter: 'blur(10px)'
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ color: '#ccc', mb: 1 }}>
              Software Engineering Intern
            </Typography>
            <Typography sx={{ color: '#999', mb: 1 }}>
              Louddoor • Columbia, SC
            </Typography>
          </Box>
          <Typography sx={{ color: '#ccc', fontSize: '0.9rem', fontWeight: 600 }}>
            02/2023 - 06/2023
          </Typography>
        </Box>
        <Typography sx={{ color: 'rgba(255,255,255,0.6)', lineHeight: 1.6, fontSize: '0.95rem' }}>
          • Assisted in writing clear documentation for code and processes.<br/>
          • Participated in code reviews to ensure quality and adherence to standards.<br/>
          • Engaged in daily stand-ups to discuss project progress and roadblocks.<br/>
          • Supported senior engineers in implementing new tools and technologies.<br/>
          • Created technical documentation such as user manuals, flowcharts, and diagrams.
        </Typography>
      </Box>

      {/* Freelance Developer */}
      <Box sx={{
        p: 3,
        border: '1px solid #666',
        borderRadius: 2,
        background: 'rgba(102,102,102,0.05)',
        backdropFilter: 'blur(10px)'
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ color: '#ccc', mb: 1 }}>
              Freelance Software Developer
            </Typography>
            <Typography sx={{ color: '#999', mb: 1 }}>
              Self-employed • Irmo, SC
            </Typography>
          </Box>
          <Typography sx={{ color: '#ccc', fontSize: '0.9rem', fontWeight: 600 }}>
            12/2020 - 02/2023
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
          {['HTML', 'CSS', 'JavaScript', 'MySQL', 'MongoDB', 'Laravel', 'AWS', 'Azure', 'GCP'].map((tech) => (
            <Box
              key={tech}
              sx={{
                px: 2,
                py: 0.5,
                border: '1px solid #666',
                borderRadius: 1,
                color: '#999',
                fontSize: '0.8rem',
                background: 'rgba(102,102,102,0.1)'
              }}
            >
              {tech}
            </Box>
          ))}
        </Box>
        <Typography sx={{ color: 'rgba(255,255,255,0.6)', lineHeight: 1.6, fontSize: '0.95rem' }}>
          • Developed mobile software solutions for local companies by analyzing client needs and utilizing various programming languages.<br/>
          • Tested and maintained software to ensure optimal performance and reliability.<br/>
          • Communicated technical information effectively to clients, ensuring satisfaction with delivered products.
        </Typography>
      </Box>

      {/* Benty Intern */}
      <Box sx={{
        p: 3,
        border: '1px solid #666',
        borderRadius: 2,
        background: 'rgba(102,102,102,0.05)',
        backdropFilter: 'blur(10px)'
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ color: '#ccc', mb: 1 }}>
              Software Engineering Intern
            </Typography>
            <Typography sx={{ color: '#999', mb: 1 }}>
              Benty • Irmo, SC
            </Typography>
          </Box>
          <Typography sx={{ color: '#ccc', fontSize: '0.9rem', fontWeight: 600 }}>
            09/2019 - 01/2023
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
          {['Java', 'Python', 'Agile'].map((tech) => (
            <Box
              key={tech}
              sx={{
                px: 2,
                py: 0.5,
                border: '1px solid #666',
                borderRadius: 1,
                color: '#999',
                fontSize: '0.8rem',
                background: 'rgba(102,102,102,0.1)'
              }}
            >
              {tech}
            </Box>
          ))}
        </Box>
        <Typography sx={{ color: 'rgba(255,255,255,0.6)', lineHeight: 1.6, fontSize: '0.95rem' }}>
          • Developed software features using Java and Python for web applications.<br/>
          • Analyzed customer requirements to design solutions that meet their needs while adhering to industry standards.<br/>
          • Collaborated with other developers on coding projects in an Agile environment.<br/>
          • Optimized existing code by refactoring it for improved readability and performance.<br/>
          • Shadowed team engineers to learn new skills.<br/>
          • Built visually rich front-end components.
        </Typography>
      </Box>

      {/* Griffin Pools */}
      <Box sx={{
        p: 3,
        border: '1px solid #666',
        borderRadius: 2,
        background: 'rgba(102,102,102,0.05)',
        backdropFilter: 'blur(10px)'
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ color: '#ccc', mb: 1 }}>
              Retail Sales Associate
            </Typography>
            <Typography sx={{ color: '#999', mb: 1 }}>
              Griffin Pools & Spas • Lexington, SC
            </Typography>
          </Box>
          <Typography sx={{ color: '#ccc', fontSize: '0.9rem', fontWeight: 600 }}>
            03/2018 - 02/2023
          </Typography>
        </Box>
        <Typography sx={{ color: 'rgba(255,255,255,0.6)', lineHeight: 1.6, fontSize: '0.95rem' }}>
          • Assisted customers in selecting appropriate pool and spa products, ensuring satisfaction.<br/>
          • Educated clients on diverse product features to enhance informed purchasing decisions.<br/>
          • Cultivated strong customer relationships through exceptional service and support.
        </Typography>
      </Box>
    </Box>
  </Box>
)

// Main Component
export const CyberpunkPortfolio: React.FC = () => {
  const [menuOpen, setMenuOpen] = useState(false)
  const [activeSection, setActiveSection] = useState('about')
  
  const renderContent = () => {
    switch (activeSection) {
      case 'about': return <AboutSection />
      case 'projects': return <ProjectsSection />
      case 'experience': return <ExperienceSection />
      case 'github': return <GitHubSection />
      default: return <AboutSection />
    }
  }
  
  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #000011 0%, #001122 50%, #002244 100%)',
        color: 'white',
        overflow: 'hidden',
        position: 'relative'
      }}
    >
      {/* 3D Background - Optimized */}
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          zIndex: 0,
          opacity: 0.6
        }}
      >
        <Canvas
          camera={{ position: [0, 0, 10], fov: 75 }}
          gl={{ 
            antialias: false, 
            powerPreference: 'high-performance',
            alpha: true,
            stencil: false,
            depth: true
          }}
          dpr={Math.min(window.devicePixelRatio, 1.5)}
        >
          <CyberpunkScene />
        </Canvas>
      </Box>
      
      {/* Grid Overlay */}
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          background: `
            linear-gradient(90deg, transparent 98%, rgba(0,255,255,0.1) 100%),
            linear-gradient(0deg, transparent 98%, rgba(0,255,255,0.1) 100%)
          `,
          backgroundSize: '50px 50px',
          zIndex: 1,
          pointerEvents: 'none'
        }}
      />
      
      {/* Header */}
      <Box
        component={motion.div}
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        sx={{
          position: 'relative',
          zIndex: 10,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          p: 3,
          background: 'rgba(0,0,20,0.3)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(0,255,255,0.3)'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar
            sx={{
              width: 50,
              height: 50,
              background: 'linear-gradient(45deg, #00ffff, #ff00ff)',
              color: 'white',
              fontWeight: 700
            }}
          >
            CP
          </Avatar>
          <Typography variant="h6" sx={{ color: '#00ffff', fontWeight: 700 }}>
            CAMERON.EXE
          </Typography>
        </Box>
        
        <IconButton
          onClick={() => setMenuOpen(true)}
          sx={{
            color: '#00ffff',
            border: '1px solid #00ffff',
            '&:hover': { background: 'rgba(0,255,255,0.1)' }
          }}
        >
          <Menu />
        </IconButton>
      </Box>
      
      {/* Main Content */}
      <Box
        component={motion.div}
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        sx={{
          position: 'relative',
          zIndex: 10,
          p: 4,
          maxWidth: 1200,
          mx: 'auto'
        }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={activeSection}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
          >
            {renderContent()}
          </motion.div>
        </AnimatePresence>
      </Box>
      
      <NavigationMenu
        isOpen={menuOpen}
        onClose={() => setMenuOpen(false)}
        activeSection={activeSection}
        setActiveSection={setActiveSection}
      />
    </Box>
  )
}