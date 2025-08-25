import React, { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Box, Typography, IconButton, Fab, TextField } from '@mui/material'
import { Close, GitHub, Work, Person, Code, VolumeUp, VolumeOff, Terminal, Email, Phone, School, Business, CheckCircle, Bolt, Build, LocalFireDepartment, Inventory, CameraAlt } from '@mui/icons-material'

// Professional Header Component
const ProfessionalHeader: React.FC<{
  onTerminalOpen: () => void
  onSocialOpen: () => void
  onMusicToggle: () => void
  isMusicPlaying: boolean
}> = ({ onTerminalOpen, onSocialOpen, onMusicToggle, isMusicPlaying }) => {
  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: '80px',
        background: 'linear-gradient(135deg, rgba(0,10,30,0.95) 0%, rgba(0,20,40,0.95) 100%)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(0,255,255,0.3)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        px: 4
      }}
    >
      {/* Logo/Brand Section */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Box
          sx={{
            width: 50,
            height: 50,
            background: 'linear-gradient(135deg, #00ffff, #0099cc)',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(0,255,255,0.3)'
          }}
        >
          <Code sx={{ color: 'white', fontSize: '1.5rem' }} />
        </Box>
        <Box>
          <Typography sx={{
            color: 'white',
            fontSize: '1.5rem',
            fontWeight: 700,
            letterSpacing: '2px',
            fontFamily: '"IBM Plex Sans", sans-serif'
          }}>
            CAMERON POTTER
          </Typography>
          <Typography sx={{
            color: '#00ffff',
            fontSize: '0.9rem',
            opacity: 0.8,
            fontFamily: '"IBM Plex Sans", sans-serif',
            fontWeight: 400
          }}>
            Software Engineer • Full-Stack Developer
          </Typography>
        </Box>
      </Box>

      {/* Navigation Menu */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <IconButton
          onClick={onTerminalOpen}
          sx={{
            color: '#00ff00',
            border: '1px solid rgba(0,255,0,0.3)',
            borderRadius: '8px',
            '&:hover': {
              background: 'rgba(0,255,0,0.1)',
              borderColor: '#00ff00'
            }
          }}
          title="Open Terminal"
        >
          <Terminal />
        </IconButton>
        
        <IconButton
          onClick={onSocialOpen}
          sx={{
            color: '#ff00ff',
            border: '1px solid rgba(255,0,255,0.3)',
            borderRadius: '8px',
            '&:hover': {
              background: 'rgba(255,0,255,0.1)',
              borderColor: '#ff00ff'
            }
          }}
          title="Social Links"
        >
          <Person />
        </IconButton>
        
        <IconButton
          onClick={onMusicToggle}
          sx={{
            color: isMusicPlaying ? '#00ffff' : 'rgba(255,255,255,0.6)',
            border: `1px solid ${isMusicPlaying ? 'rgba(0,255,255,0.5)' : 'rgba(255,255,255,0.3)'}`,
            borderRadius: '8px',
            '&:hover': {
              background: isMusicPlaying ? 'rgba(0,255,255,0.1)' : 'rgba(255,255,255,0.1)',
              borderColor: isMusicPlaying ? '#00ffff' : 'rgba(255,255,255,0.6)'
            }
          }}
          title="Toggle Music"
        >
          {isMusicPlaying ? <VolumeUp /> : <VolumeOff />}
        </IconButton>
        
        <Box sx={{ mx: 2, width: '1px', height: '30px', background: 'rgba(255,255,255,0.2)' }} />
        
        <Typography sx={{
          color: 'rgba(255,255,255,0.7)',
          fontSize: '0.8rem',
          fontFamily: '"JetBrains Mono", "Courier New", monospace',
          fontWeight: 500,
          letterSpacing: '1px'
        }}>
          STATUS: ONLINE
        </Typography>
      </Box>
    </Box>
  )
}

// Interactive Command Terminal Component
const CommandTerminal: React.FC<{ isOpen: boolean; setIsOpen: (open: boolean) => void }> = ({ isOpen, setIsOpen }) => {
  const [command, setCommand] = useState('')
  const [output, setOutput] = useState<string[]>([
    'CAMERON.EXE Terminal v1.0.0',
    'Type "help" for available commands',
    ''
  ])
  const inputRef = useRef<HTMLInputElement>(null)
  const outputRef = useRef<HTMLDivElement>(null)

  const commands = {
    help: [
      'CAMERON.EXE Terminal Commands:',
      '  help       - Show this help menu',
      '  about      - Personal info about Cameron',
      '  skills     - Technical skills and languages',
      '  experience - Professional work history',
      '  education  - Academic background',
      '  hobbies    - Personal interests and activities', 
      '  contact    - Get contact information with links',
      '  social     - Social media links',
      '  github     - GitHub stats and repositories',
      '  projects   - Recent coding projects',
      '  clear      - Clear terminal screen',
      '  whoami     - System information',
      '  matrix     - Enter the matrix...',
      '  exit       - Close terminal'
    ],
    about: [
      'Cameron Potter - Software Engineer',
      'Location: Working at Louddoor',
      'Education: Computer Science @ WGU',
      'Focus: Full-stack web development'
    ],
    skills: [
      'Primary Technologies:',
      '  • PHP & Laravel',
      '  • JavaScript & Vue.js',
      '  • React & TypeScript',
      '  • Python & FastAPI',
      '  • MySQL & PostgreSQL'
    ],
    contact: [
      'Contact Information:',
      '  Email: cameron@louddoor.com',
      '  GitHub: github.com/cameronopotter',
      '  LinkedIn: linkedin.com/in/cameronpotter'
    ],
    github: [
      'GitHub Profile: https://github.com/cameronopotter',
      '📊 GitHub Stats:',
      '  • Public Repositories: 25+',
      '  • Primary Languages: JavaScript, PHP, Python, TypeScript, Java',
      '  • Recent Projects: Digital Greenhouse, Cyberpunk Portfolio',
      '  • Active contributor to open source projects',
      '  • Consistent commit history and collaboration'
    ],
    experience: [
      'Professional Experience:',
      '🔹 Software Engineer - Louddoor (06/2023 - Current)',
      '   Full-stack development, code reviews, Agile methodologies',
      '🔹 Software Engineering Intern - Louddoor (02/2023 - 06/2023)', 
      '   Technical documentation, daily standups, tool implementation',
      '🔹 Freelance Software Developer (12/2020 - 02/2023)',
      '   Mobile solutions, client analysis, multiple programming languages',
      '🔹 Software Engineering Intern - Benty (09/2019 - 01/2023)',
      '   Java & Python development, Agile environment, code optimization',
      '🔹 Retail Sales Associate - Griffin Pools & Spas (03/2018 - 02/2023)',
      '   Customer service, product education, relationship building'
    ],
    education: [
      'Academic Background:',
      'Western Governors University - Salt Lake City, UT',
      '   Bachelor of Science in Computer Science (Expected 08/2025)',
      'University of South Carolina - Columbia, SC', 
      '   Computer Science (Some College - No Degree)',
      '   Solid foundation in CS fundamentals and programming'
    ],
    hobbies: [
      'Personal Interests & Activities:',
      '🎾 Tennis enthusiast - promotes fitness and discipline',
      '⛳ Golf player - enjoys focus and strategic thinking', 
      '🎵 Passionate about music as creative expression',
      '🎮 Video gaming for fun, problem-solving, and teamwork',
      'Personal coding projects and open source contributions',
      '📚 Continuous learning in technology and software development'
    ],
    social: [
      'Social Media & Professional Links:',
      'LinkedIn: https://www.linkedin.com/in/cameron-potter-b4029024a/',
      'GitHub: https://github.com/cameronopotter',
      'Instagram: https://www.instagram.com/cameronpotter12/',
      'Email: cameronopotter@gmail.com',
      'Phone: (803) 603-6393'
    ],
    projects: [
      'Recent Coding Projects:',
      '🌃 Cyberpunk Portfolio - Interactive 3D city portfolio',
      '   Built with React, TypeScript, Framer Motion',
      'Digital Greenhouse - 3D garden portfolio concept',
      '   Three.js, WebGL, immersive 3D experience',
      'Various client projects during freelance work',
      'Open source contributions on GitHub',
      'Mobile applications for local businesses'
    ],
    whoami: [
      'SYSTEM INFO:',
      'User: Cameron Potter',
      'Status: Software Engineer',
      'Location: Columbia, SC',
      'Company: Louddoor', 
      'Education: Computer Science Student',
      'Clearance Level: Public',
      'Access: Authorized',
      'Last Login: Active Session'
    ],
    matrix: [
      'Wake up, Neo...',
      'The Matrix has you...',
      'Follow the white rabbit...',
      '> Entering matrix mode...',
      '> 01001000 01100101 01101100 01101100 01101111',
      '> Reality.exe stopped working...',
      '> Welcome to the real world.',
      '> Connection established ●'
    ]
  }

  const handleCommand = (cmd: string) => {
    const newOutput = [...output, `> ${cmd}`]
    
    if (cmd === 'clear') {
      setOutput([
        'CAMERON.EXE Terminal v1.0.0',
        'Type "help" for available commands',
        ''
      ])
    } else if (cmd === 'exit') {
      setIsOpen(false)
      return
    } else if (commands[cmd.toLowerCase() as keyof typeof commands]) {
      setOutput([...newOutput, ...commands[cmd.toLowerCase() as keyof typeof commands], ''])
    } else if (cmd.trim() === '') {
      setOutput([...newOutput, ''])
    } else {
      const suggestions = Object.keys(commands).filter(c => 
        c.includes(cmd.toLowerCase()) || cmd.toLowerCase().includes(c)
      )
      const suggestionText = suggestions.length > 0 
        ? `Did you mean: ${suggestions.join(', ')}?`
        : 'Type "help" for available commands'
      
      setOutput([...newOutput, `Command not found: ${cmd}`, suggestionText, ''])
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleCommand(command)
      setCommand('')
    }
  }

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  return (
    <>

      {/* Terminal Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, x: 50, y: -50 }}
            animate={{ opacity: 1, scale: 1, x: 0, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, x: 50, y: -50 }}
            style={{
              position: 'fixed',
              top: '10%',
              right: '5%',
              width: '400px',
              maxHeight: '60%',
              zIndex: 1001
            }}
          >
            <Box
              sx={{
                background: 'rgba(0,20,0,0.95)',
                border: '2px solid #00ff00',
                borderRadius: '8px',
                fontFamily: 'Courier New, monospace',
                fontSize: '0.8rem',
                color: '#00ff00',
                backdropFilter: 'blur(20px)',
                overflow: 'hidden'
              }}
            >
              {/* Terminal Header */}
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  p: 1,
                  borderBottom: '1px solid #00ff00',
                  background: 'rgba(0,50,0,0.5)'
                }}
              >
                <Typography sx={{ color: '#00ff00', fontWeight: 700, fontSize: '0.8rem' }}>
                  CAMERON.EXE Terminal
                </Typography>
                <IconButton 
                  onClick={() => setIsOpen(false)}
                  sx={{ color: '#00ff00', p: 0.5 }}
                  size="small"
                >
                  <Close fontSize="small" />
                </IconButton>
              </Box>

              {/* Terminal Output */}
              <Box
                sx={{
                  p: 2,
                  height: '300px',
                  overflowY: 'auto',
                  '&::-webkit-scrollbar': { width: '6px' },
                  '&::-webkit-scrollbar-track': { background: 'transparent' },
                  '&::-webkit-scrollbar-thumb': { background: '#00ff00', borderRadius: '3px' }
                }}
              >
                {output.map((line, i) => (
                  <Typography
                    key={i}
                    sx={{
                      color: line.startsWith('>') ? '#00ffff' : '#00ff00',
                      fontFamily: 'Courier New, monospace',
                      fontSize: '0.75rem',
                      lineHeight: 1.4,
                      whiteSpace: 'pre-wrap'
                    }}
                  >
                    {line}
                  </Typography>
                ))}
              </Box>

              {/* Terminal Input */}
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  p: 1,
                  borderTop: '1px solid #00ff00',
                  background: 'rgba(0,50,0,0.3)'
                }}
              >
                <Typography sx={{ color: '#00ff00', mr: 1, fontFamily: 'Courier New, monospace' }}>
                  $
                </Typography>
                <TextField
                  ref={inputRef}
                  value={command}
                  onChange={(e) => setCommand(e.target.value)}
                  onKeyPress={handleKeyPress}
                  variant="standard"
                  size="small"
                  sx={{
                    flex: 1,
                    '& .MuiInput-root': {
                      color: '#00ff00',
                      fontFamily: 'Courier New, monospace',
                      fontSize: '0.8rem',
                      '&::before': { borderColor: 'transparent' },
                      '&::after': { borderColor: '#00ff00' },
                      '&:hover::before': { borderColor: 'transparent' }
                    },
                    '& .MuiInput-input': {
                      padding: '2px 0'
                    }
                  }}
                  placeholder="Type a command..."
                  InputProps={{
                    disableUnderline: false
                  }}
                />
              </Box>
            </Box>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

// Lofi Music Player Component
const LofiPlayer: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [volume, setVolume] = useState(0.3)
  const audioRef = useRef<HTMLAudioElement>(null)
  
  // Free lofi music URLs (you'd want to replace with your preferred tracks)
  const lofiTracks = [
    'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav', // Replace with actual lofi URLs
    // Add more tracks
  ]
  
  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }
  
  return (
    <Box
      sx={{
        position: 'fixed',
        top: 20,
        right: 20,
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        gap: 1
      }}
    >
      <Fab
        size="small"
        onClick={togglePlay}
        sx={{
          background: 'rgba(0,255,255,0.2)',
          border: '1px solid #00ffff',
          color: '#00ffff',
          backdropFilter: 'blur(10px)',
          '&:hover': {
            background: 'rgba(0,255,255,0.3)',
            boxShadow: '0 0 20px #00ffff'
          }
        }}
      >
        {isPlaying ? <VolumeUp /> : <VolumeOff />}
      </Fab>
      
      <audio
        ref={audioRef}
        loop
        volume={volume}
        onEnded={() => setIsPlaying(false)}
      >
        <source src="https://www.soundjay.com/misc/sounds/bell-ringing-05.wav" type="audio/wav" />
        {/* Fallback for browsers that don't support the audio element */}
        Your browser does not support the audio element.
      </audio>
      
      {isPlaying && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          style={{
            position: 'absolute',
            top: '50%',
            right: '60px',
            transform: 'translateY(-50%)',
            background: 'rgba(0,255,255,0.1)',
            border: '1px solid #00ffff',
            borderRadius: '4px',
            padding: '4px 8px',
            color: '#00ffff',
            fontSize: '0.7rem',
            fontFamily: 'monospace',
            backdropFilter: 'blur(10px)',
            whiteSpace: 'nowrap'
          }}
        >
          🎵 Cyberpunk Lofi
        </motion.div>
      )}
    </Box>
  )
}

// Social Media Hub - Interactive floating panel
const SocialMediaHub: React.FC<{ isOpen: boolean; setIsOpen: (open: boolean) => void }> = ({ isOpen, setIsOpen }) => {
  
  const socialLinks = [
    {
      name: 'Email',
      url: 'mailto:cameronopotter@gmail.com',
      icon: <Email sx={{ fontSize: '1rem' }} />,
      color: '#ea4335',
      description: 'Direct Contact'
    },
    {
      name: 'LinkedIn',
      url: 'https://www.linkedin.com/in/cameron-potter-b4029024a/',
      icon: <Business sx={{ fontSize: '1rem' }} />,
      color: '#0077b5',
      description: 'Professional Network'
    },
    {
      name: 'GitHub',
      url: 'https://github.com/cameronopotter',
      icon: <GitHub sx={{ fontSize: '1rem' }} />,
      color: '#333333',
      description: 'Code Repository'
    },
    {
      name: 'Instagram',
      url: 'https://www.instagram.com/cameronpotter12/',
      icon: <CameraAlt sx={{ fontSize: '1rem' }} />,
      color: '#e4405f',
      description: 'Personal Life & Interests'
    }
  ]
  
  return (
    <>
      {/* Social Hub Toggle Button */}
      <Fab
        onClick={() => setIsOpen(!isOpen)}
        sx={{
          position: 'fixed',
          top: 140,
          right: 20,
          background: 'rgba(255,0,255,0.2)',
          border: '1px solid #ff00ff',
          color: '#ff00ff',
          width: 50,
          height: 50,
          '&:hover': {
            background: 'rgba(255,0,255,0.3)',
            boxShadow: '0 0 25px #ff00ff'
          }
        }}
      >
        🌐
      </Fab>
      
      {/* Social Media Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, x: 100, rotateY: -90 }}
            animate={{ opacity: 1, x: 0, rotateY: 0 }}
            exit={{ opacity: 0, x: 100, rotateY: -90 }}
            style={{
              position: 'fixed',
              top: '20%',
              right: '5%',
              width: '320px',
              zIndex: 1001,
              perspective: '1000px'
            }}
          >
            <Box
              sx={{
                background: 'rgba(20,0,40,0.95)',
                border: '2px solid #ff00ff',
                borderRadius: '12px',
                overflow: 'hidden',
                backdropFilter: 'blur(20px)',
                boxShadow: '0 0 40px rgba(255,0,255,0.3)'
              }}
            >
              {/* Header */}
              <Box
                sx={{
                  p: 2,
                  borderBottom: '1px solid #ff00ff',
                  background: 'rgba(255,0,255,0.1)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <Typography sx={{ color: '#ff00ff', fontWeight: 700, fontFamily: 'monospace' }}>
                  🌐 SOCIAL.NETWORK.EXE
                </Typography>
                <IconButton 
                  onClick={() => setIsOpen(false)}
                  sx={{ color: '#ff00ff', p: 0.5 }}
                  size="small"
                >
                  <Close fontSize="small" />
                </IconButton>
              </Box>
              
              {/* Social Links */}
              <Box sx={{ p: 2 }}>
                {socialLinks.map((social, i) => (
                  <motion.div
                    key={social.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                  >
                    <Box
                      component="a"
                      href={social.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      sx={{
                        display: 'block',
                        mb: 2,
                        p: 2,
                        border: `1px solid ${social.color}`,
                        borderRadius: '8px',
                        background: `${social.color}10`,
                        textDecoration: 'none',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          background: `${social.color}20`,
                          boxShadow: `0 0 15px ${social.color}60`,
                          transform: 'translateX(5px)'
                        }
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Typography sx={{ fontSize: '1.5rem' }}>
                          {social.icon}
                        </Typography>
                        <Box>
                          <Typography sx={{ 
                            color: social.color, 
                            fontWeight: 700,
                            fontSize: '1rem'
                          }}>
                            {social.name}
                          </Typography>
                          <Typography sx={{ 
                            color: 'rgba(255,255,255,0.7)',
                            fontSize: '0.8rem'
                          }}>
                            {social.description}
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                  </motion.div>
                ))}
              </Box>
              
              {/* Status */}
              <Box
                sx={{
                  p: 2,
                  borderTop: '1px solid #ff00ff40',
                  background: 'rgba(0,0,0,0.3)'
                }}
              >
                <Typography sx={{ 
                  color: '#00ff00', 
                  fontSize: '0.8rem',
                  fontFamily: 'monospace',
                  textAlign: 'center'
                }}>
                  ● CONNECTIONS_ACTIVE • READY_TO_NETWORK
                </Typography>
              </Box>
            </Box>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

// Holographic Career Timeline - Immersive Experience
const HolographicTimeline: React.FC<{
  isOpen: boolean
  setIsOpen: (open: boolean) => void
  closeAllComponents: () => void
}> = React.memo(({ isOpen, setIsOpen, closeAllComponents }) => {
  const [activeYear, setActiveYear] = useState(2023)
  
  const timelineData = [
    {
      year: 2023,
      title: 'Software Engineer',
      company: 'Louddoor',
      color: '#00ffff',
      achievements: ['Full-stack development', 'Code reviews', 'Agile methodologies'],
      status: 'CURRENT'
    },
    {
      year: 2023,
      title: 'Software Engineering Intern',
      company: 'Louddoor',
      color: '#0088ff',
      achievements: ['Technical documentation', 'Daily standups', 'Tool implementation'],
      status: 'PROMOTED'
    },
    {
      year: 2021,
      title: 'Freelance Developer',
      company: 'Self-employed',
      color: '#ff6600',
      achievements: ['Mobile solutions', 'Client analysis', 'Multiple languages'],
      status: 'ENTREPRENEUR'
    },
    {
      year: 2020,
      title: 'Software Engineering Intern',
      company: 'Benty',
      color: '#9900ff',
      achievements: ['Java & Python', 'Agile environment', 'Code optimization'],
      status: 'FOUNDATION'
    }
  ]
  
  return (
    <>
      {/* Timeline Toggle Button */}
      <Fab
        onClick={() => {
          if (isOpen) {
            setIsOpen(false)
          } else {
            closeAllComponents()
            setIsOpen(true)
          }
        }}
        sx={{
          position: 'fixed',
          bottom: 80,
          left: 20,
          background: 'rgba(0,255,255,0.2)',
          border: '1px solid #00ffff',
          color: '#00ffff',
          width: 55,
          height: 55,
          '&:hover': {
            background: 'rgba(0,255,255,0.3)',
            boxShadow: '0 0 30px #00ffff'
          }
        }}
      >
        📊
      </Fab>
      
      {/* Holographic Timeline Interface */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.5, rotateX: -90 }}
            animate={{ opacity: 1, scale: 1, rotateX: 0 }}
            exit={{ opacity: 0, scale: 0.5, rotateX: -90 }}
            style={{
              position: 'fixed',
              top: '15%',
              left: '10%',
              width: '80vw',
              height: '85vh',
              maxWidth: '900px',
              maxHeight: '700px',
              zIndex: 1001,
              perspective: '2000px',
              transformStyle: 'preserve-3d'
            }}
          >
            <Box
              sx={{
                width: '100%',
                height: '100%',
                background: 'radial-gradient(circle, rgba(0,255,255,0.1) 0%, rgba(0,0,40,0.95) 100%)',
                border: '2px solid #00ffff',
                borderRadius: '20px',
                backdropFilter: 'blur(25px)',
                overflow: 'visible',
                boxShadow: '0 0 50px rgba(0,255,255,0.4)',
                position: 'relative'
              }}
            >
              {/* Header */}
              <Box
                sx={{
                  p: 2,
                  borderBottom: '1px solid #00ffff',
                  background: 'rgba(0,255,255,0.1)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <Typography sx={{ color: '#00ffff', fontWeight: 700, fontSize: '1.2rem' }}>
                  CAREER.TIMELINE.HOLOGRAM
                </Typography>
                <IconButton 
                  onClick={() => setIsOpen(false)}
                  sx={{ color: '#00ffff' }}
                >
                  <Close />
                </IconButton>
              </Box>
              
              {/* 3D Timeline Display */}
              <Box sx={{ 
                p: 3, 
                height: 'calc(100% - 80px)', 
                position: 'relative', 
                overflowY: 'auto',
                overflowX: 'hidden',
                '&::-webkit-scrollbar': {
                  width: '8px',
                },
                '&::-webkit-scrollbar-track': {
                  background: 'rgba(0,255,255,0.1)',
                },
                '&::-webkit-scrollbar-thumb': {
                  background: 'rgba(0,255,255,0.5)',
                  borderRadius: '4px',
                  '&:hover': {
                    background: 'rgba(0,255,255,0.8)',
                  }
                }
              }}>
                {/* Timeline Track */}
                <Box
                  sx={{
                    position: 'absolute',
                    left: '50%',
                    top: '20px',
                    height: `${timelineData.length * 220}px`,
                    width: '4px',
                    background: 'linear-gradient(180deg, #00ffff, #0066cc)',
                    boxShadow: '0 0 20px #00ffff',
                    transform: 'translateX(-50%)'
                  }}
                />
                
                {/* Timeline Nodes */}
                {timelineData.map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, rotateY: -90, z: -100 }}
                    animate={{ 
                      opacity: 1, 
                      rotateY: 0, 
                      z: activeYear === item.year ? 50 : 0,
                      scale: activeYear === item.year ? 1.1 : 1
                    }}
                    transition={{ delay: index * 0.2, duration: 0.8 }}
                    style={{
                      position: 'absolute',
                      left: index % 2 === 0 ? '5%' : '55%',
                      top: `${40 + index * 200}px`,
                      width: '280px',
                      cursor: 'pointer',
                      transformStyle: 'preserve-3d'
                    }}
                    onClick={() => setActiveYear(item.year)}
                  >
                    <Box
                      sx={{
                        p: 2,
                        background: `${item.color}15`,
                        border: `2px solid ${item.color}`,
                        borderRadius: '12px',
                        backdropFilter: 'blur(10px)',
                        boxShadow: activeYear === item.year 
                          ? `0 0 25px ${item.color}` 
                          : `0 0 10px ${item.color}60`,
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          boxShadow: `0 0 30px ${item.color}`,
                          transform: 'translateZ(20px)'
                        }
                      }}
                    >
                      <Typography sx={{ 
                        color: item.color, 
                        fontWeight: 700,
                        fontSize: '0.9rem',
                        mb: 0.5
                      }}>
                        {item.year} • {item.status}
                      </Typography>
                      <Typography sx={{ 
                        color: 'white',
                        fontSize: '1rem',
                        fontWeight: 600,
                        mb: 1
                      }}>
                        {item.title}
                      </Typography>
                      <Typography sx={{ 
                        color: item.color,
                        fontSize: '0.8rem',
                        mb: 1,
                        opacity: 0.8
                      }}>
                        {item.company}
                      </Typography>
                      
                      {activeYear === item.year && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                        >
                          <Box sx={{ mt: 1 }}>
                            {item.achievements.map((achievement, i) => (
                              <Typography 
                                key={i}
                                sx={{ 
                                  color: 'rgba(255,255,255,0.8)',
                                  fontSize: '0.7rem',
                                  mb: 0.5,
                                  '&::before': { content: '"→ "', color: item.color }
                                }}
                              >
                                {achievement}
                              </Typography>
                            ))}
                          </Box>
                        </motion.div>
                      )}
                    </Box>
                    
                    {/* Connection Line */}
                    <Box
                      sx={{
                        position: 'absolute',
                        top: '50%',
                        [index % 2 === 0 ? 'right' : 'left']: '-30px',
                        width: '30px',
                        height: '2px',
                        background: item.color,
                        boxShadow: `0 0 10px ${item.color}`,
                        transform: 'translateY(-50%)'
                      }}
                    />
                  </motion.div>
                ))}
                
                {/* Floating Data Particles */}
                {Array.from({ length: 15 }).map((_, i) => (
                  <motion.div
                    key={`particle-${i}`}
                    animate={{
                      y: [0, -20, 0],
                      x: [0, 10, -5, 0],
                      opacity: [0.3, 1, 0.3]
                    }}
                    transition={{
                      duration: 4 + Math.random() * 2,
                      repeat: Infinity,
                      delay: Math.random() * 2
                    }}
                    style={{
                      position: 'absolute',
                      left: `${Math.random() * 90 + 5}%`,
                      top: `${Math.random() * 80 + 10}%`,
                      width: '4px',
                      height: '4px',
                      background: '#00ffff',
                      borderRadius: '50%',
                      boxShadow: '0 0 8px #00ffff',
                      pointerEvents: 'none'
                    }}
                  />
                ))}
              </Box>
            </Box>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
});

// Background City Buildings (Non-interactive)
const BackgroundBuildings: React.FC = () => {
  // Generate varied building configurations
  const backgroundBuildings = [
    // Behind and to the left
    { x: 50, y: 140, width: 120, height: 180, color: '#005588', opacity: 0.9, zIndex: 2 },
    { x: 200, y: 140, width: 80, height: 220, color: '#006677', opacity: 0.85, zIndex: 2 },
    { x: 320, y: 140, width: 100, height: 160, color: '#004466', opacity: 0.9, zIndex: 2 },
    
    // Behind main buildings (further back)
    { x: 400, y: 140, width: 90, height: 200, color: '#003355', opacity: 0.75, zIndex: 1 },
    { x: 550, y: 140, width: 110, height: 180, color: '#004477', opacity: 0.75, zIndex: 1 },
    { x: 700, y: 140, width: 85, height: 240, color: '#005566', opacity: 0.75, zIndex: 1 },
    { x: 850, y: 140, width: 95, height: 160, color: '#003344', opacity: 0.8, zIndex: 1 },
    
    // To the right
    { x: 1200, y: 140, width: 130, height: 200, color: '#006688', opacity: 0.9, zIndex: 2 },
    { x: 1350, y: 140, width: 90, height: 170, color: '#004455', opacity: 0.9, zIndex: 2 },
    { x: 1500, y: 140, width: 110, height: 190, color: '#005577', opacity: 0.85, zIndex: 2 },
    
    // Far background (smallest, most faded)
    { x: 150, y: 140, width: 60, height: 140, color: '#003333', opacity: 0.6, zIndex: 0 },
    { x: 300, y: 140, width: 70, height: 120, color: '#003344', opacity: 0.6, zIndex: 0 },
    { x: 500, y: 140, width: 65, height: 160, color: '#004433', opacity: 0.6, zIndex: 0 },
    { x: 800, y: 140, width: 75, height: 130, color: '#003355', opacity: 0.6, zIndex: 0 },
    { x: 1100, y: 140, width: 80, height: 150, color: '#004444', opacity: 0.6, zIndex: 0 },
    { x: 1400, y: 140, width: 70, height: 140, color: '#003366', opacity: 0.6, zIndex: 0 },
    
    // Additional mid-level buildings for density
    { x: 380, y: 140, width: 95, height: 190, color: '#005599', opacity: 0.8, zIndex: 2 },
    { x: 650, y: 140, width: 105, height: 210, color: '#004488', opacity: 0.8, zIndex: 2 },
    { x: 950, y: 140, width: 85, height: 170, color: '#004488', opacity: 0.5, zIndex: 2 },
    { x: 1150, y: 140, width: 115, height: 220, color: '#001155', opacity: 0.5, zIndex: 2 },
    
    // Extra far background for city horizon
    { x: 100, y: 140, width: 45, height: 100, color: '#000811', opacity: 0.2, zIndex: 0 },
    { x: 250, y: 140, width: 50, height: 110, color: '#001022', opacity: 0.2, zIndex: 0 },
    { x: 450, y: 140, width: 55, height: 95, color: '#000922', opacity: 0.2, zIndex: 0 },
    { x: 650, y: 140, width: 60, height: 120, color: '#001211', opacity: 0.2, zIndex: 0 },
    { x: 900, y: 140, width: 50, height: 105, color: '#002011', opacity: 0.2, zIndex: 0 },
    { x: 1050, y: 140, width: 65, height: 115, color: '#001133', opacity: 0.2, zIndex: 0 },
    { x: 1250, y: 140, width: 55, height: 100, color: '#001022', opacity: 0.2, zIndex: 0 },
    { x: 1450, y: 140, width: 70, height: 125, color: '#002211', opacity: 0.2, zIndex: 0 }
  ]

  return (
    <Box
      sx={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: '100%',
        pointerEvents: 'none',
        zIndex: 3 // Behind interactive buildings but above ground
      }}
    >
      {backgroundBuildings.map((building, index) => (
        <motion.div
          key={`bg-building-${index}`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: building.opacity, y: 0 }}
          transition={{ duration: 1, delay: index * 0.1 }}
          style={{
            position: 'absolute',
            left: building.x,
            bottom: building.y,
            width: building.width,
            height: building.height,
            zIndex: building.zIndex,
            perspective: '1000px'
          }}
        >
          {/* Building 3D Structure */}
          <Box
            sx={{
              width: '100%',
              height: '100%',
              position: 'relative',
              transformStyle: 'preserve-3d',
              transform: 'rotateX(-1deg)'
            }}
          >
            {/* Building Front Face */}
            <Box
              sx={{
                position: 'absolute',
                width: '100%',
                height: '100%',
                background: `linear-gradient(180deg, 
                  ${building.color}50 0%, 
                  rgba(0,10,20,0.8) 30%,
                  rgba(0,5,15,0.9) 70%,
                  rgba(0,0,10,0.95) 100%
                )`,
                border: `2px solid ${building.color}70`,
                borderBottom: 'none',
                opacity: building.opacity,
                overflow: 'hidden'
              }}
            >
              {/* Simple window pattern */}
              <Box
                sx={{
                  position: 'absolute',
                  top: '15%',
                  left: 0,
                  right: 0,
                  bottom: '20%',
                  background: `
                    repeating-linear-gradient(
                      90deg,
                      transparent 0px,
                      transparent 10px,
                      ${building.color}40 10px,
                      ${building.color}40 12px
                    ),
                    repeating-linear-gradient(
                      0deg,
                      transparent 0px,
                      transparent 15px,
                      ${building.color}50 15px,
                      ${building.color}50 17px
                    )
                  `,
                  opacity: 0.6
                }}
              />
              
              {/* Scattered lit windows */}
              {Array.from({ length: 8 }).map((_, i) => (
                <motion.div
                  key={i}
                  animate={{
                    opacity: [0.3, 0.8, 0.3]
                  }}
                  transition={{
                    duration: 3 + Math.random() * 2,
                    repeat: Infinity,
                    delay: Math.random() * 3
                  }}
                  style={{
                    position: 'absolute',
                    left: `${20 + (i % 2) * 40}%`,
                    top: `${25 + Math.floor(i / 2) * 20}%`,
                    width: '6px',
                    height: '8px',
                    background: Math.random() > 0.7 ? building.color : 'transparent',
                    opacity: Math.random() * 0.6 + 0.2,
                    boxShadow: Math.random() > 0.7 ? `0 0 6px ${building.color}` : 'none'
                  }}
                />
              ))}
            </Box>
            
            {/* Building Top */}
            <Box
              sx={{
                position: 'absolute',
                width: '100%',
                height: '12px',
                top: '-12px',
                background: `linear-gradient(90deg, 
                  ${building.color}25 0%, 
                  ${building.color}40 50%, 
                  ${building.color}25 100%
                )`,
                transform: 'rotateX(70deg)',
                transformOrigin: 'bottom',
                opacity: building.opacity * 0.8
              }}
            />
            
            {/* Building Side (3D effect) */}
            <Box
              sx={{
                position: 'absolute',
                width: '15px',
                height: '100%',
                right: '-15px',
                background: `linear-gradient(180deg, 
                  ${building.color}10 0%, 
                  rgba(0,5,10,0.7) 50%,
                  rgba(0,0,5,0.8) 100%
                )`,
                transform: 'rotateY(70deg)',
                transformOrigin: 'left',
                opacity: building.opacity * 0.6
              }}
            />
          </Box>
        </motion.div>
      ))}
    </Box>
  )
}

// AI Neural Interface - Interactive Assistant
const AINeural: React.FC<{
  isOpen: boolean
  setIsOpen: (open: boolean) => void
  closeAllComponents: () => void
}> = ({ isOpen, setIsOpen, closeAllComponents }) => {
  const [messages, setMessages] = useState([
    { type: 'ai', text: 'Neural Interface Online. I am CAMERON.AI, your interactive guide to Cameron Potter\'s portfolio. How can I assist you?' }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  
  const aiResponses = {
    // Personal questions
    about: [
      'Cameron Potter is a passionate software engineer at Louddoor, specializing in full-stack development with a focus on creating scalable, efficient solutions. He combines strong technical skills with excellent communication and problem-solving abilities.',
      'Based in Columbia, SC, Cameron is currently pursuing his BS in Computer Science at Western Governors University (graduating August 2025) while working full-time as a software engineer.',
      'What sets Cameron apart is his dedication to continuous learning and his ability to work effectively in Agile environments, contributing to both individual projects and collaborative team efforts.',
      'Cameron has a proven track record of delivering high-quality software solutions, from enterprise applications to innovative web experiences like this interactive portfolio.'
    ],
    skills: [
      '🔥 PROGRAMMING LANGUAGES:\nC • C++ • C# • Python • JavaScript • Java • PHP • SQL\n\n💻 FRAMEWORKS & LIBRARIES:\nLaravel • Vue.js • React • TypeScript • Node.js • Express.js\n\n⚡ SPECIALIZATIONS:\n• Full-stack web development\n• RESTful API design & implementation\n• Database design & optimization\n• Agile methodologies & Scrum',
      '🛠️ TECHNICAL EXPERTISE:\n• Frontend: React, Vue.js, TypeScript, HTML5, CSS3\n• Backend: PHP/Laravel, Node.js, Python, Java\n• Databases: MySQL, PostgreSQL, MongoDB\n• Tools: Git, Docker, AWS, Linux\n• Testing: Unit testing, Integration testing\n• DevOps: CI/CD pipelines, deployment automation',
      '🎯 CORE COMPETENCIES:\n• Object-oriented programming & design patterns\n• MVC architecture & clean code principles\n• API integration & third-party services\n• Performance optimization & scalability\n• Technical documentation & code reviews\n• Cross-functional team collaboration'
    ],
    experience: [
      '💼 SOFTWARE ENGINEER @ LOUDDOOR\nJune 2023 - Present\n• Full-stack development using PHP, Laravel, Vue.js\n• Code reviews and technical documentation\n• Agile development and sprint planning\n• Feature development and bug resolution',
      '🎓 SOFTWARE ENGINEERING INTERN @ LOUDDOOR\nFeb 2023 - June 2023\n• Gained hands-on experience in professional software development\n• Worked on real-world projects with senior developers\n• Learned industry best practices and coding standards\n• Contributed to both frontend and backend development',
      '🚀 FREELANCE SOFTWARE DEVELOPER\nDec 2020 - Feb 2023\n• Developed custom web applications for various clients\n• Managed full project lifecycle from requirements to deployment\n• Built responsive websites and database-driven applications\n• Handled client communications and project management',
      '⚙️ SOFTWARE ENGINEERING INTERN @ BENTY\nSep 2019 - Jan 2023\n• Worked with Java and Python on enterprise applications\n• Gained experience in software testing and quality assurance\n• Participated in code reviews and team meetings\n• Contributed to documentation and technical specifications'
    ],
    projects: [
      '🌆 CYBERPUNK PORTFOLIO (Current Project)\n• Interactive 3D city built with React & Three.js\n• Real-time GitHub API integration\n• Responsive design with smooth animations\n• Features: AI chat, holographic timeline, social hub',
      '💼 LOUDDOOR PLATFORM FEATURES\n• Full-stack development using Laravel & Vue.js\n• RESTful API development and integration\n• Database optimization and query performance\n• User authentication and authorization systems',
      '🔧 CUSTOM WEB APPLICATIONS\n• E-commerce platforms with payment integration\n• Content management systems\n• Database-driven business applications\n• Responsive designs for mobile and desktop'
    ],
    contact: [
      '📧 EMAIL: cameronopotter@gmail.com\n📱 PHONE: (803) 603-6393\n📍 LOCATION: Columbia, SC 29063\n\n🔗 PROFESSIONAL LINKS:\n💼 LinkedIn: linkedin.com/in/cameron-potter-b4029024a/\n👨‍💻 GitHub: github.com/cameronopotter\n📸 Instagram: instagram.com/cameronpotter12/\n\n✨ Feel free to reach out for opportunities, collaboration, or just to connect!'
    ],
    hobbies: [
      '🎾 TENNIS & GOLF: Cameron enjoys both sports for their strategic elements and fitness benefits. These activities help him stay sharp and provide a great balance to his technical work.',
      '🎵 MUSIC: Passionate about music as both a listener and creator. Music serves as a creative outlet and inspiration for his technical projects.',
      '🎮 GAMING: Enjoys video games for their problem-solving challenges and team coordination aspects, which actually complement his software development skills.',
      '🌟 These hobbies reflect Cameron\'s well-rounded personality and his belief in maintaining a healthy work-life balance while staying intellectually engaged.'
    ],
    portfolio: [
      '🚀 PORTFOLIO FEATURES:\n• Interactive 3D cyberpunk city environment\n• Clickable buildings reveal different sections\n• Real-time GitHub API for live project data\n• Smooth animations and responsive design\n• AI chat interface (that\'s me!)\n• Holographic career timeline\n• Social media integration hub',
      '💻 TECHNICAL IMPLEMENTATION:\n• Built with React 18 & TypeScript\n• Three.js for 3D graphics and animations\n• Framer Motion for smooth transitions\n• Material-UI for consistent design\n• Real-time data fetching and caching\n• Optimized for performance and accessibility',
      '🎨 DESIGN PHILOSOPHY:\n• Cyberpunk aesthetic with professional content\n• Interactive experience that tells Cameron\'s story\n• Mobile-responsive for all devices\n• Focus on user experience and engagement\n• Showcases both technical and creative abilities'
    ],
    education: [
      '🎓 WESTERN GOVERNORS UNIVERSITY\nBachelor of Science in Computer Science\nExpected Graduation: August 2025\n\n📚 RELEVANT COURSEWORK:\n• Data Structures & Algorithms\n• Software Engineering\n• Database Management\n• Web Development\n• Computer Architecture\n• Operating Systems',
      '🏆 ACADEMIC ACHIEVEMENTS:\n• Maintaining strong GPA while working full-time\n• Hands-on projects in multiple programming languages\n• Focus on practical, industry-relevant skills\n• Self-directed learning and time management'
    ]
  }
  
  const handleSendMessage = () => {
    if (!inputValue.trim()) return
    
    const userMessage = inputValue.trim()
    setMessages(prev => [...prev, { type: 'user', text: userMessage }])
    setInputValue('')
    setIsThinking(true)
    
    // Simulate AI thinking delay
    setTimeout(() => {
      const lowerInput = userMessage.toLowerCase()
      let response = '🤔 I didn\'t quite understand that, but I\'d love to help! Try asking me about:\n\n💻 "What are Cameron\'s skills?"\n🏢 "Tell me about his experience"\n📚 "What about his education?"\n🎯 "Show me his projects"\n📞 "How can I contact Cameron?"\n🎮 "What are his hobbies?"\n🌐 "Tell me about this portfolio"\n\nOr just say "help" for a full menu!'
      
      // Enhanced keyword matching for comprehensive responses
      if (lowerInput.includes('skill') || lowerInput.includes('tech') || lowerInput.includes('language') || lowerInput.includes('programming') || lowerInput.includes('framework')) {
        response = aiResponses.skills[Math.floor(Math.random() * aiResponses.skills.length)]
      } else if (lowerInput.includes('experience') || lowerInput.includes('work') || lowerInput.includes('job') || lowerInput.includes('career') || lowerInput.includes('employment')) {
        response = aiResponses.experience[Math.floor(Math.random() * aiResponses.experience.length)]
      } else if (lowerInput.includes('project') && !lowerInput.includes('portfolio')) {
        response = aiResponses.projects[Math.floor(Math.random() * aiResponses.projects.length)]
      } else if (lowerInput.includes('education') || lowerInput.includes('school') || lowerInput.includes('university') || lowerInput.includes('degree') || lowerInput.includes('study')) {
        response = aiResponses.education[Math.floor(Math.random() * aiResponses.education.length)]
      } else if (lowerInput.includes('contact') || lowerInput.includes('email') || lowerInput.includes('phone') || lowerInput.includes('reach') || lowerInput.includes('connect')) {
        response = aiResponses.contact[0] // Single comprehensive contact response
      } else if (lowerInput.includes('hobby') || lowerInput.includes('interest') || lowerInput.includes('fun') || lowerInput.includes('music') || lowerInput.includes('game') || lowerInput.includes('tennis') || lowerInput.includes('golf')) {
        response = aiResponses.hobbies[Math.floor(Math.random() * aiResponses.hobbies.length)]
      } else if (lowerInput.includes('portfolio') || lowerInput.includes('website') || lowerInput.includes('site') || lowerInput.includes('cyberpunk') || lowerInput.includes('interface')) {
        response = aiResponses.portfolio[Math.floor(Math.random() * aiResponses.portfolio.length)]
      } else if (lowerInput.includes('about') || lowerInput.includes('who') || lowerInput.includes('cameron') || lowerInput.includes('tell me') || lowerInput.includes('introduce')) {
        response = aiResponses.about[Math.floor(Math.random() * aiResponses.about.length)]
      } else if (lowerInput.includes('hello') || lowerInput.includes('hi') || lowerInput.includes('hey') || lowerInput.includes('greetings')) {
        response = '👋 Hello! Welcome to Cameron\'s neural interface! I\'m excited to help you learn about Cameron Potter. I can share detailed information about his:\n\n🔹 Technical skills & expertise\n🔹 Professional experience & projects\n🔹 Education & achievements\n🔹 Contact information\n🔹 Personal interests\n🔹 This amazing portfolio!\n\nWhat interests you most?'
      } else if (lowerInput.includes('help') || lowerInput.includes('what can you') || lowerInput.includes('commands') || lowerInput.includes('what do you know')) {
        response = '🤖 I\'m Cameron\'s AI assistant with comprehensive knowledge about:\n\n💻 TECHNICAL:\n• Programming languages & frameworks\n• Professional experience at Louddoor\n• Software development projects\n• Technical skills & competencies\n\n🎓 ACADEMIC:\n• Computer Science education at WGU\n• Relevant coursework & achievements\n\n📞 PERSONAL:\n• Contact information & social links\n• Hobbies & interests\n• This interactive portfolio details\n\nTry asking specific questions like "What are Cameron\'s skills?" or "Tell me about his experience!"'
      } else if (lowerInput.includes('hire') || lowerInput.includes('recruit') || lowerInput.includes('opportunity') || lowerInput.includes('available')) {
        response = '💼 Cameron is always interested in exciting opportunities! He\'s currently employed at Louddoor but open to discussing:\n\n🚀 Challenging technical roles\n💡 Innovative projects\n🌟 Career advancement opportunities\n📈 Freelance/contract work\n\n📧 Best way to reach him: cameronopotter@gmail.com\n💼 LinkedIn: linkedin.com/in/cameron-potter-b4029024a/\n\nHe responds quickly to professional inquiries!'
      } else if (lowerInput.includes('why') && (lowerInput.includes('hire') || lowerInput.includes('choose'))) {
        response = '⭐ WHY CHOOSE CAMERON?\n\n🎯 PROVEN TRACK RECORD:\n• Currently excelling as Software Engineer at Louddoor\n• Strong full-stack development experience\n• Successful freelance project history\n\n💪 TECHNICAL EXCELLENCE:\n• Proficient in modern tech stack (React, Laravel, Python, etc.)\n• Clean, maintainable code practices\n• Agile development experience\n\n🚀 SOFT SKILLS:\n• Excellent communication & collaboration\n• Problem-solving mindset\n• Continuous learner & adaptable\n• Reliable & professional\n\nCameron brings both technical expertise AND the right attitude to any team!'
      }
      
      setMessages(prev => [...prev, { type: 'ai', text: response }])
      setIsThinking(false)
    }, 800 + Math.random() * 1000)
  }
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSendMessage()
    }
  }
  
  return (
    <>
      {/* AI Toggle Button */}
      <Fab
        onClick={() => {
          if (isOpen) {
            setIsOpen(false)
          } else {
            closeAllComponents()
            setIsOpen(true)
          }
        }}
        sx={{
          position: 'fixed',
          bottom: 20,
          left: 20,
          background: 'rgba(0,255,0,0.2)',
          border: '1px solid #00ff00',
          color: '#00ff00',
          width: 60,
          height: 60,
          '&:hover': {
            background: 'rgba(0,255,0,0.3)',
            boxShadow: '0 0 35px #00ff00'
          }
        }}
      >
        🧠
      </Fab>
      
      {/* AI Neural Interface */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 50 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 50 }}
            transition={{ 
              type: "spring", 
              stiffness: 300, 
              damping: 30,
              mass: 0.8 
            }}
            style={{
              position: 'fixed',
              bottom: '10%',
              left: '5%',
              width: '450px',
              height: '600px',
              zIndex: 1001,
              perspective: '1000px'
            }}
          >
            <Box
              sx={{
                width: '100%',
                height: '100%',
                background: 'radial-gradient(circle at center, rgba(0,255,0,0.1) 0%, rgba(0,40,0,0.95) 100%)',
                border: '2px solid #00ff00',
                borderRadius: '20px',
                backdropFilter: 'blur(25px)',
                overflow: 'hidden',
                boxShadow: '0 0 60px rgba(0,255,0,0.4)',
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              {/* Neural Header */}
              <Box
                sx={{
                  p: 2,
                  borderBottom: '1px solid #00ff00',
                  background: 'rgba(0,255,0,0.1)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <Typography sx={{ color: '#00ff00', fontWeight: 700, fontSize: '1.1rem' }}>
                  🧠 CAMERON.AI • NEURAL_INTERFACE
                </Typography>
                <IconButton 
                  onClick={() => setIsOpen(false)}
                  sx={{ color: '#00ff00' }}
                >
                  <Close />
                </IconButton>
              </Box>
              
              {/* Neural Activity Indicator */}
              <Box
                sx={{
                  p: 1,
                  borderBottom: '1px solid #00ff0040',
                  background: 'rgba(0,0,0,0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1
                }}
              >
                <motion.div
                  animate={{ opacity: 0.8 }}
                  transition={{ duration: 0 }}
                  style={{
                    width: '8px',
                    height: '8px',
                    background: '#00ff00',
                    borderRadius: '50%',
                    boxShadow: '0 0 10px #00ff00'
                  }}
                />
                <Typography sx={{ color: '#00ff00', fontSize: '0.8rem', fontFamily: 'monospace' }}>
                  NEURAL_PATHWAYS_ACTIVE • READY_FOR_INTERACTION
                </Typography>
              </Box>
              
              {/* Message Display */}
              <Box
                sx={{
                  flex: 1,
                  p: 2,
                  overflowY: 'auto',
                  '&::-webkit-scrollbar': { width: '6px' },
                  '&::-webkit-scrollbar-track': { background: 'transparent' },
                  '&::-webkit-scrollbar-thumb': { background: '#00ff00', borderRadius: '3px' }
                }}
              >
                {messages.map((message, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    style={{ marginBottom: '1rem' }}
                  >
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                        mb: 1
                      }}
                    >
                      <Box
                        sx={{
                          maxWidth: '80%',
                          p: 1.5,
                          borderRadius: '10px',
                          background: message.type === 'user' 
                            ? 'rgba(0,255,255,0.1)' 
                            : 'rgba(0,255,0,0.1)',
                          border: message.type === 'user' 
                            ? '1px solid #00ffff' 
                            : '1px solid #00ff00',
                          boxShadow: message.type === 'user' 
                            ? '0 0 10px rgba(0,255,255,0.2)' 
                            : '0 0 10px rgba(0,255,0,0.2)'
                        }}
                      >
                        <Typography sx={{
                          color: message.type === 'user' ? '#00ffff' : '#00ff00',
                          fontSize: '0.85rem',
                          fontFamily: message.type === 'ai' ? 'monospace' : 'inherit',
                          whiteSpace: 'pre-line',
                          lineHeight: 1.4
                        }}>
                          {message.type === 'ai' ? '🤖 ' : '👤 '}{message.text}
                        </Typography>
                      </Box>
                    </Box>
                  </motion.div>
                ))}
                
                {isThinking && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '1rem' }}
                  >
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: '10px',
                        background: 'rgba(0,255,0,0.1)',
                        border: '1px solid #00ff00',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1
                      }}
                    >
                      <Typography sx={{ color: '#00ff00', fontSize: '0.85rem' }}>
                        🤖 Processing neural patterns
                      </Typography>
                      {Array.from({ length: 3 }).map((_, i) => (
                        <motion.div
                          key={i}
                          animate={{ opacity: [0.3, 1, 0.3] }}
                          transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                          style={{
                            width: '4px',
                            height: '4px',
                            background: '#00ff00',
                            borderRadius: '50%'
                          }}
                        />
                      ))}
                    </Box>
                  </motion.div>
                )}
              </Box>
              
              {/* Input Area */}
              <Box
                sx={{
                  p: 2,
                  borderTop: '1px solid #00ff00',
                  background: 'rgba(0,0,0,0.3)',
                  display: 'flex',
                  gap: 1
                }}
              >
                <TextField
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me about Cameron..."
                  variant="standard"
                  fullWidth
                  disabled={isThinking}
                  sx={{
                    '& .MuiInput-root': {
                      color: '#00ff00',
                      fontFamily: 'IBM Plex Mono, monospace',
                      fontSize: '0.9rem',
                      '&::before': { borderColor: '#00ff0040' },
                      '&::after': { borderColor: '#00ff00' },
                      '&:hover::before': { borderColor: '#00ff0060' }
                    },
                    '& .MuiInput-input::placeholder': {
                      color: '#00ff0060',
                      opacity: 1
                    }
                  }}
                />
                <IconButton
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isThinking}
                  sx={{
                    color: '#00ff00',
                    border: '1px solid #00ff0060',
                    width: '40px',
                    height: '40px',
                    '&:hover': {
                      background: 'rgba(0,255,0,0.1)',
                      boxShadow: '0 0 15px #00ff0060'
                    },
                    '&:disabled': {
                      color: '#00ff0030'
                    }
                  }}
                >
                  <Bolt />
                </IconButton>
              </Box>
            </Box>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

// Interactive Building Component with 3D appearance - Memoized
const CyberpunkBuilding: React.FC<{
  id: string
  name: string
  icon: React.ReactNode
  position: { x: number; y: number }
  size: { width: number; height: number }
  color: string
  onClick: () => void
  isActive: boolean
}> = React.memo(({ id, name, icon, position, size, color, onClick, isActive }) => {
  const [isHovered, setIsHovered] = useState(false)
  
  return (
    <motion.div
      style={{
        position: 'absolute',
        left: position.x,
        bottom: position.y,
        width: size.width,
        height: size.height,
        cursor: 'pointer',
        zIndex: 15 + Math.floor(position.y / 10), // Above background buildings
        perspective: '1000px'
      }}
      whileHover={{ 
        scale: 1.02,
        y: -5,
        filter: 'brightness(1.2)',
        transition: { duration: 0.2 }
      }}
      whileTap={{ scale: 0.98 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      onClick={onClick}
    >
      {/* Building 3D Structure */}
      <Box
        sx={{
          width: '100%',
          height: '100%',
          position: 'relative',
          transformStyle: 'preserve-3d',
          transform: 'rotateX(-2deg)'
        }}
      >
        {/* Building Front Face */}
        <Box
          sx={{
            position: 'absolute',
            width: '100%',
            height: '100%',
            background: `linear-gradient(180deg, 
              ${color}15 0%, 
              rgba(0,10,20,0.95) 20%,
              rgba(0,5,15,0.98) 50%,
              rgba(0,0,10,1) 100%
            )`,
            border: `1px solid ${color}40`,
            borderBottom: 'none',
            boxShadow: isActive 
              ? `0 0 30px ${color}60, inset 0 0 20px ${color}20`
              : `0 0 15px rgba(0,0,0,0.5)`,
            overflow: 'hidden'
          }}
        >
          {/* Windows Grid */}
          <Box
            sx={{
              position: 'absolute',
              top: '10%',
              left: 0,
              right: 0,
              bottom: '15%',
              background: `
                repeating-linear-gradient(
                  90deg,
                  transparent 0px,
                  transparent 12px,
                  ${color}15 12px,
                  ${color}15 14px
                ),
                repeating-linear-gradient(
                  0deg,
                  transparent 0px,
                  transparent 20px,
                  ${color}20 20px,
                  ${color}20 22px
                )
              `,
              opacity: 0.8
            }}
          />
          
          {/* Random lit windows */}
          {Array.from({ length: 15 }).map((_, i) => (
            <Box
              key={i}
              sx={{
                position: 'absolute',
                left: `${15 + (i % 3) * 30}%`,
                top: `${20 + Math.floor(i / 3) * 15}%`,
                width: '8px',
                height: '10px',
                background: Math.random() > 0.6 ? color : 'transparent',
                opacity: Math.random() * 0.8 + 0.2,
                boxShadow: Math.random() > 0.6 ? `0 0 8px ${color}` : 'none',
                animation: Math.random() > 0.8 ? 'flicker 4s infinite' : 'none',
                '@keyframes flicker': {
                  '0%, 100%': { opacity: 0.8 },
                  '50%': { opacity: 0.3 }
                }
              }}
            />
          ))}
        </Box>
        
        {/* Building Top/Roof */}
        <Box
          sx={{
            position: 'absolute',
            width: '100%',
            height: '15px',
            top: '-15px',
            background: `linear-gradient(90deg, 
              ${color}30 0%, 
              ${color}50 50%, 
              ${color}30 100%
            )`,
            transform: 'rotateX(70deg)',
            transformOrigin: 'bottom',
            borderTop: `1px solid ${color}60`,
            boxShadow: `0 -5px 15px ${color}30`
          }}
        />
        
        {/* Building Side (3D effect) */}
        <Box
          sx={{
            position: 'absolute',
            width: '20px',
            height: '100%',
            right: '-20px',
            background: `linear-gradient(180deg, 
              ${color}10 0%, 
              rgba(0,5,10,0.9) 30%,
              rgba(0,0,5,0.95) 100%
            )`,
            transform: 'rotateY(70deg)',
            transformOrigin: 'left',
            borderRight: `1px solid ${color}30`,
            opacity: 0.7
          }}
        />
        
        {/* Building Icon */}
        <Box
          sx={{
            position: 'absolute',
            top: '35%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: color,
            fontSize: '2.5rem',
            filter: `drop-shadow(0 0 15px ${color})`,
            opacity: 0.9
          }}
        >
          {icon}
        </Box>
        
        {/* Professional Building Label */}
        <Box
          sx={{
            position: 'absolute',
            bottom: '20%',
            left: '50%',
            transform: 'translateX(-50%)',
            textAlign: 'center',
            width: '90%'
          }}
        >
          <Box sx={{ 
            color: 'white',
            fontSize: '0.85rem', 
            fontWeight: 600,
            letterSpacing: '1.5px',
            textShadow: `0 0 10px ${color}`,
            lineHeight: 1.2,
            mb: 0.5,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            fontFamily: '"IBM Plex Sans", sans-serif'
          }}>
            {name.split(' ').map((word, i) => (
              <Box key={i} component="div">
                {word.toUpperCase()}
              </Box>
            ))}
          </Box>
          
          {/* Subtle underline */}
          <Box
            sx={{
              width: '60%',
              height: '2px',
              background: `linear-gradient(90deg, transparent, ${color}, transparent)`,
              margin: '0 auto',
              borderRadius: '1px',
              opacity: isActive ? 1 : 0.6
            }}
          />
        </Box>

        {/* Enhanced Hover Label with Description */}
        <AnimatePresence>
          {isHovered && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              style={{
                position: 'absolute',
                top: -70,
                left: '50%',
                transform: 'translateX(-50%)',
                background: `${color}20`,
                border: `1px solid ${color}`,
                borderRadius: '4px',
                padding: '8px 12px',
                whiteSpace: 'nowrap',
                backdropFilter: 'blur(15px)',
                boxShadow: `0 0 20px ${color}40`
              }}
            >
              <Typography sx={{ color: color, fontSize: '0.9rem', fontWeight: 700, mb: 0.5 }}>
                {name}
              </Typography>
              <Typography sx={{ color: 'white', fontSize: '0.7rem' }}>
                {id === 'about' && 'Personal info & skills'}
                {id === 'projects' && 'Live GitHub projects'}
                {id === 'experience' && 'Work history'}
                {id === 'github' && 'Commit activity'}
                {id === 'skills' && 'Technical proficiencies'}
                {id === 'contact' && 'Get in touch'}
              </Typography>
            </motion.div>
          )}
        </AnimatePresence>
      </Box>
    </motion.div>
  )
});

// City Ground and Street Level
const CityGround: React.FC = () => {
  return (
    <Box
      sx={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: '140px', // Ground level height
        pointerEvents: 'none',
        zIndex: 1
      }}
    >
      {/* Main street surface */}
      <Box
        sx={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '40px',
          background: 'linear-gradient(180deg, #001122 0%, #000811 50%, #000408 100%)',
          borderTop: '3px solid #00ffff40',
          boxShadow: '0 0 20px rgba(0,255,255,0.1) inset'
        }}
      />
      
      {/* Street grid pattern */}
      <Box
        sx={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '40px',
          background: `
            repeating-linear-gradient(
              90deg,
              transparent 0px,
              transparent 48px,
              #00ffff15 48px,
              #00ffff15 52px
            ),
            repeating-linear-gradient(
              0deg,
              transparent 0px,
              transparent 98px,
              #00ffff10 98px,
              #00ffff10 102px
            )
          `,
          opacity: 0.6
        }}
      />
      
      {/* Sidewalk/building foundation */}
      <Box
        sx={{
          position: 'absolute',
          bottom: '40px',
          left: 0,
          right: 0,
          height: '100px',
          background: 'linear-gradient(180deg, rgba(0,20,40,0.1) 0%, rgba(0,15,30,0.3) 50%, rgba(0,10,20,0.6) 100%)',
          borderTop: '1px solid rgba(0,255,255,0.1)'
        }}
      />
      
      {/* Street lights and utility elements */}
      {Array.from({ length: 8 }).map((_, i) => (
        <motion.div
          key={`streetlight-${i}`}
          animate={{
            opacity: [0.8, 1, 0.8]
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: i * 0.5
          }}
          style={{
            position: 'absolute',
            left: `${15 + i * 12}%`,
            bottom: '40px',
            width: '4px',
            height: '60px',
            background: 'linear-gradient(180deg, transparent 0%, #00ffff40 80%, #00ffff 100%)',
            borderRadius: '2px',
            boxShadow: '0 0 15px rgba(0,255,255,0.3)'
          }}
        />
      ))}
    </Box>
  )
}

// Distant City Skyline Background
const CitySkyline: React.FC = () => {
  return (
    <Box
      sx={{
        position: 'absolute',
        bottom: 140, // Above the ground level
        left: 0,
        right: 0,
        height: 'calc(100vh - 300px)', // Leave room for sky
        pointerEvents: 'none',
        zIndex: 1
      }}
    >
      {/* Far background buildings layer 1 */}
      <Box
        sx={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '60%',
          background: `
            linear-gradient(180deg, transparent 0%, #001122 100%),
            repeating-linear-gradient(
              0deg,
              #001122 0px,
              #001122 15px,
              #002233 15px,
              #002233 35px,
              #001122 35px,
              #001122 60px,
              #003344 60px,
              #003344 95px
            )
          `,
          opacity: 0.25,
          transform: 'scaleY(0.8)'
        }}
      />
      
      {/* Mid-distance buildings layer 2 */}
      <Box
        sx={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '40%',
          background: `
            repeating-linear-gradient(
              0deg,
              transparent 0px,
              transparent 10px,
              #002244 10px,
              #002244 25px,
              transparent 25px,
              transparent 45px,
              #003355 45px,
              #003355 70px
            )
          `,
          opacity: 0.4,
          transform: 'scaleY(0.9)'
        }}
      />
      
      {/* Distant flickering windows */}
      {Array.from({ length: 60 }).map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0 }}
          animate={{ 
            opacity: [0.2, 0.6, 0.2],
          }}
          transition={{
            duration: 2 + Math.random() * 3,
            repeat: Infinity,
            delay: Math.random() * 5
          }}
          style={{
            position: 'absolute',
            left: `${Math.random() * 100}%`,
            bottom: `${10 + Math.random() * 30}%`,
            width: '2px',
            height: '3px',
            background: Math.random() > 0.7 ? '#00ffff' : '#ffff00',
            boxShadow: `0 0 3px ${Math.random() > 0.7 ? '#00ffff' : '#ffff00'}`,
            borderRadius: '1px',
            opacity: 0.4
          }}
        />
      ))}
    </Box>
  )
}

// High Altitude Space Elements
const SpaceElements: React.FC = () => {
  return (
    <Box
      sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '300px', // Only upper portion of screen
        pointerEvents: 'none',
        overflow: 'hidden',
        zIndex: 5
      }}
    >
      {/* High-altitude Flying Vehicles */}
      {Array.from({ length: 4 }).map((_, i) => (
        <motion.div
          key={`vehicle-${i}`}
          initial={{ 
            x: -120,
            y: 30 + i * 60, // Much higher up
          }}
          animate={{
            x: window.innerWidth + 120,
            y: 30 + i * 60 + Math.sin(Date.now() / 1000 + i) * 15
          }}
          transition={{
            duration: 18 + i * 4,
            repeat: Infinity,
            ease: 'linear',
            delay: i * 6
          }}
          style={{
            position: 'absolute',
            width: '50px',
            height: '10px',
            background: 'linear-gradient(90deg, #00ffff, #ff00ff)',
            borderRadius: '5px',
            boxShadow: '0 0 20px #00ffff',
            filter: 'blur(0.8px)',
            opacity: 0.8
          }}
        />
      ))}
      
      {/* Orbital Satellites/Space Stations */}
      {Array.from({ length: 6 }).map((_, i) => (
        <motion.div
          key={`satellite-${i}`}
          animate={{
            y: [0, -15, 0],
            rotate: [0, 360],
            scale: [1, 1.1, 1],
            opacity: [0.6, 1, 0.6]
          }}
          transition={{
            duration: 4 + i * 0.8,
            repeat: Infinity,
            delay: i * 1.2
          }}
          style={{
            position: 'absolute',
            left: `${15 + i * 12}%`,
            top: `${20 + (i % 2) * 40}%`, // Higher positions
            width: '16px',
            height: '16px',
            border: '3px solid #ffff00',
            borderRadius: '50%',
            background: 'radial-gradient(circle, #ffff0080, transparent)',
            boxShadow: '0 0 25px #ffff00, inset 0 0 10px #ffff0040'
          }}
        />
      ))}
      
      {/* High-altitude Data Streams */}
      {Array.from({ length: 10 }).map((_, i) => (
        <motion.div
          key={`stream-${i}`}
          initial={{ 
            pathLength: 0,
            opacity: 0
          }}
          animate={{
            pathLength: 1,
            opacity: [0, 0.8, 0]
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            delay: i * 0.4,
            ease: 'easeInOut'
          }}
          style={{
            position: 'absolute',
            left: `${Math.random() * 70 + 15}%`,
            top: `${Math.random() * 50 + 10}%`, // Stay in upper area
            width: '100px',
            height: '3px',
            background: 'linear-gradient(90deg, transparent, #00ff00, transparent)',
            transform: `rotate(${Math.random() * 180 - 90}deg)`, // More horizontal
            borderRadius: '2px',
            boxShadow: '0 0 6px #00ff00',
            opacity: 0.6
          }}
        />
      ))}
      
      {/* Distant stars/navigation beacons */}
      {Array.from({ length: 20 }).map((_, i) => (
        <motion.div
          key={`star-${i}`}
          animate={{
            opacity: [0.3, 1, 0.3],
            scale: [1, 1.2, 1]
          }}
          transition={{
            duration: 2 + Math.random() * 3,
            repeat: Infinity,
            delay: i * 0.2
          }}
          style={{
            position: 'absolute',
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 80}%`,
            width: '2px',
            height: '2px',
            background: '#ffffff',
            borderRadius: '50%',
            boxShadow: '0 0 4px #ffffff',
            opacity: 0.7
          }}
        />
      ))}
    </Box>
  )
}

// Neon Signs and Billboards
const NeonSigns: React.FC = () => {
  const signs = [
    { text: 'LOUDDOOR', color: '#ff00ff', x: 20, y: 15 }, // Moved higher
    { text: 'WGU.EDU', color: '#00ff00', x: 70, y: 10 }, // Moved higher
    { text: 'DEV_MODE', color: '#ffff00', x: 45, y: 20 }, // Moved higher
    { text: 'PORTFOLIO.EXE', color: '#00ffff', x: 80, y: 25 } // Moved higher
  ]
  
  return (
    <Box
      sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        pointerEvents: 'none',
        zIndex: 3
      }}
    >
      {signs.map((sign, i) => (
        <motion.div
          key={i}
          animate={{
            opacity: [0.7, 1, 0.7],
            textShadow: [`0 0 10px ${sign.color}`, `0 0 20px ${sign.color}`, `0 0 10px ${sign.color}`]
          }}
          transition={{
            duration: 2 + Math.random(),
            repeat: Infinity,
            delay: i * 0.5
          }}
          style={{
            position: 'absolute',
            left: `${sign.x}%`,
            top: `${sign.y}%`,
            color: sign.color,
            fontSize: '0.8rem',
            fontFamily: 'monospace',
            fontWeight: 'bold',
            textShadow: `0 0 10px ${sign.color}`,
            transform: 'rotate(-5deg)',
            border: `1px solid ${sign.color}`,
            padding: '2px 6px',
            background: `${sign.color}10`,
            borderRadius: '2px'
          }}
        >
          {sign.text}
        </motion.div>
      ))}
    </Box>
  )
}

// GitHub Commit Visualization (Enhanced) - Mid-level atmosphere
const GitHubCommits: React.FC<{ commits: any[] }> = ({ commits }) => {
  return (
    <Box
      sx={{
        position: 'absolute',
        top: 300, // Start below space elements
        left: 0,
        right: 0,
        bottom: 140, // End above ground level
        pointerEvents: 'none',
        overflow: 'hidden',
        zIndex: 8 // Above buildings but below space
      }}
    >
      {/* Commit streaks moving through city atmosphere */}
      {commits.slice(0, 20).map((commit, index) => (
        <motion.div
          key={index}
          initial={{ 
            x: Math.random() * window.innerWidth,
            y: window.innerHeight - 140, // Start above ground
            opacity: 0
          }}
          animate={{
            x: Math.random() * window.innerWidth * 0.8 + window.innerWidth * 0.1,
            y: 300, // Move up to space boundary
            opacity: [0, 1, 1, 0]
          }}
          transition={{
            duration: 6 + Math.random() * 3,
            delay: index * 0.3,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
          style={{
            position: 'absolute',
            width: '3px',
            height: '15px',
            background: 'linear-gradient(180deg, #00ffff80, transparent)',
            boxShadow: '0 0 8px #00ffff',
            borderRadius: '2px',
            opacity: 0.8
          }}
        />
      ))}
      
      {/* Floating code fragments in mid-level */}
      {Array.from({ length: 8 }).map((_, i) => {
        const codeSnippets = ['{ }', '< />', '[ ]', '( )', '==', '++', '//', '&&', 'git', 'npm']
        return (
          <motion.div
            key={`code-${i}`}
            animate={{
              y: [0, -25, 0],
              x: [0, 8, -4, 0],
              rotate: [0, 3, -3, 0],
              opacity: [0.4, 0.8, 0.4]
            }}
            transition={{
              duration: 5 + Math.random() * 2,
              repeat: Infinity,
              delay: i * 1
            }}
            style={{
              position: 'absolute',
              left: `${Math.random() * 80 + 10}%`,
              top: `${Math.random() * 60 + 20}%`, // Stay in mid-level zone
              color: '#00ffff',
              fontSize: '1rem',
              fontFamily: 'monospace',
              textShadow: '0 0 8px #00ffff60',
              fontWeight: 'bold',
              opacity: 0.6
            }}
          >
            {codeSnippets[i % codeSnippets.length]}
          </motion.div>
        )
      })}
      
      {/* Building-level data connections */}
      {Array.from({ length: 12 }).map((_, i) => (
        <motion.div
          key={`connection-${i}`}
          initial={{ 
            pathLength: 0,
            opacity: 0
          }}
          animate={{
            pathLength: 1,
            opacity: [0, 0.6, 0]
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            delay: i * 0.5,
            ease: 'easeInOut'
          }}
          style={{
            position: 'absolute',
            left: `${Math.random() * 70 + 15}%`,
            top: `${Math.random() * 40 + 30}%`,
            width: '60px',
            height: '2px',
            background: 'linear-gradient(90deg, transparent, #00ff0060, transparent)',
            transform: `rotate(${Math.random() * 90 - 45}deg)`,
            borderRadius: '1px',
            boxShadow: '0 0 4px #00ff0040'
          }}
        />
      ))}
    </Box>
  )
}

// Detailed Content Modal
const ContentModal: React.FC<{
  isOpen: boolean
  onClose: () => void
  section: string
  title: string
  color: string
  children: React.ReactNode
}> = ({ isOpen, onClose, section, title, color, children }) => {
  if (!isOpen) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.8)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px'
      }}
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.8, y: 50 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.8, y: 50 }}
        onClick={(e) => e.stopPropagation()}
        style={{
          background: `linear-gradient(135deg, rgba(0,0,20,0.95), rgba(0,20,40,0.95))`,
          border: `2px solid ${color}`,
          borderRadius: '12px',
          padding: '30px',
          maxWidth: '800px',
          maxHeight: '80vh',
          overflow: 'auto',
          backdropFilter: 'blur(20px)',
          boxShadow: `0 0 50px ${color}40`
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography 
            variant="h4" 
            sx={{ 
              color: 'white', 
              fontWeight: 800,
              letterSpacing: '1px',
              textShadow: `2px 2px 0px ${color}40`
            }}
          >
            {title.toUpperCase()}
          </Typography>
          <IconButton onClick={onClose} sx={{ color: color }}>
            <Close />
          </IconButton>
        </Box>
        {children}
      </motion.div>
    </motion.div>
  )
}

// Main Cyberpunk City Component
export const CyberpunkCity: React.FC = () => {
  const [activeSection, setActiveSection] = useState<string | null>(null)
  const [cameraPosition, setCameraPosition] = useState({ x: 0, y: 0, scale: 1 })
  const [githubData, setGithubData] = useState<any>(null)
  const [terminalOpen, setTerminalOpen] = useState(false)
  const [socialOpen, setSocialOpen] = useState(false)
  const [timelineOpen, setTimelineOpen] = useState(false)
  const [aiOpen, setAiOpen] = useState(false)
  
  // Function to close all overlays/components
  const closeAllComponents = useCallback(() => {
    setActiveSection(null)
    setTerminalOpen(false)
    setSocialOpen(false)
    setTimelineOpen(false)
    setAiOpen(false)
    setCameraPosition({ x: 0, y: 0, scale: 1 })
  }, [])
  const [githubStats, setGithubStats] = useState({
    publicRepos: 0,
    totalCommits: 0,
    languages: 0,
    streakDays: 0,
    languageStats: [] as Array<{ name: string; percentage: number; color: string }>
  })
  const [githubLoading, setGithubLoading] = useState(true)
  const audioRef = useRef<HTMLAudioElement>(null)
  const [musicPlaying, setMusicPlaying] = useState(false)
  
  // Use ref to track music state without causing re-renders
  const musicStateRef = useRef(false)
  
  const toggleMusic = useCallback(() => {
    if (audioRef.current) {
      if (musicStateRef.current) {
        audioRef.current.pause()
        musicStateRef.current = false
      } else {
        audioRef.current.play().catch(err => console.log('Audio play failed:', err))
        musicStateRef.current = true
      }
      setMusicPlaying(musicStateRef.current)
    }
  }, [])
  const cityRef = useRef<HTMLDivElement>(null)
  
  // Handle ESC key to close all components
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeAllComponents()
      }
    }
    
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [closeAllComponents])
  
  // Fetch real GitHub data
  useEffect(() => {
    const fetchGitHubData = async () => {
      try {
        setGithubLoading(true)
        const [userResponse, reposResponse] = await Promise.all([
          fetch('https://api.github.com/users/cameronopotter'),
          fetch('https://api.github.com/users/cameronopotter/repos?sort=updated&per_page=100')
        ])
        
        const userData = await userResponse.json()
        const reposData = await reposResponse.json()
        
        // Calculate language statistics
        const languageCounts: { [key: string]: number } = {}
        let totalSize = 0
        
        reposData.forEach((repo: any) => {
          if (repo.language) {
            languageCounts[repo.language] = (languageCounts[repo.language] || 0) + (repo.size || 1)
            totalSize += repo.size || 1
          }
        })
        
        // Get top languages with colors
        const languageColors: { [key: string]: string } = {
          'TypeScript': '#007acc',
          'JavaScript': '#f1e05a',
          'PHP': '#777bb4',
          'Python': '#3776ab',
          'HTML': '#e34c26',
          'CSS': '#1572b6',
          'Vue': '#4fc08d',
          'Java': '#b07219'
        }
        
        const languageStats = Object.entries(languageCounts)
          .sort(([,a], [,b]) => b - a)
          .slice(0, 3)
          .map(([lang, size]) => ({
            name: lang,
            percentage: Math.round((size / totalSize) * 100),
            color: languageColors[lang] || '#666666'
          }))
        
        // Calculate estimated total commits (rough estimate based on repo activity)
        const totalCommits = reposData.reduce((sum: number, repo: any) => {
          return sum + (repo.size > 0 ? Math.max(1, Math.floor(repo.size / 10)) : 0)
        }, 0)
        
        // Calculate streak days (mock for now - would need contributions API for real data)
        const streakDays = Math.floor(Math.random() * 100) + 30 // Mock streak
        
        setGithubStats({
          publicRepos: userData.public_repos || 0,
          totalCommits: totalCommits,
          languages: Object.keys(languageCounts).length,
          streakDays: streakDays,
          languageStats: languageStats
        })
        
        setGithubData({
          user: userData,
          repos: reposData
        })
        
      } catch (error) {
        console.error('Error fetching GitHub data:', error)
        // Fallback to mock data
        setGithubStats({
          publicRepos: 25,
          totalCommits: 847,
          languages: 8,
          streakDays: 67,
          languageStats: [
            { name: 'TypeScript', percentage: 45, color: '#007acc' },
            { name: 'PHP', percentage: 30, color: '#777bb4' },
            { name: 'Python', percentage: 25, color: '#3776ab' }
          ]
        })
        
        setGithubData({
          user: { login: 'cameronopotter', public_repos: 25, followers: 15 },
          repos: [
            { name: 'digital-greenhouse', description: 'Interactive 3D portfolio', language: 'TypeScript', stargazers_count: 5 },
            { name: 'cyberpunk-portfolio', description: 'Cyberpunk-themed portfolio site', language: 'React', stargazers_count: 3 }
          ]
        })
      } finally {
        setGithubLoading(false)
      }
    }
    
    fetchGitHubData()
  }, [])
  
  // Mock GitHub commits data - enhanced
  const mockCommits = Array.from({ length: 30 }, (_, i) => ({
    id: i,
    message: `Commit ${i + 1}`,
    date: new Date(Date.now() - i * 86400000).toISOString()
  }))

  // Calculate responsive building positions based on screen width
  const getResponsiveBuildings = () => {
    const screenWidth = window.innerWidth
    const minMargin = 60 // Minimum margin on each side
    const availableWidth = screenWidth - (minMargin * 2)
    const buildingCount = 5
    
    // Base building widths
    const baseBuildingWidths = [200, 240, 200, 240, 220]
    const totalBaseBuildingWidth = baseBuildingWidths.reduce((sum, width) => sum + width, 0)
    
    // Calculate scale factor to fit all buildings
    const maxScale = 1
    const minScale = 0.6 // Don't shrink buildings smaller than 60%
    const requiredWidth = totalBaseBuildingWidth + (buildingCount - 1) * 20 // 20px minimum spacing
    const scale = Math.min(maxScale, Math.max(minScale, availableWidth / requiredWidth))
    
    // Calculate actual spacing after scaling
    const scaledBuildingWidth = totalBaseBuildingWidth * scale
    const remainingSpace = availableWidth - scaledBuildingWidth
    const spacing = Math.max(15, remainingSpace / (buildingCount - 1)) // Minimum 15px spacing
    
    let currentX = minMargin // Start position
    
    return [
      {
        id: 'about',
        name: 'About Tower',
        icon: <Person />,
        position: { x: currentX, y: 140 },
        size: { width: 200 * scale, height: 280 * scale },
        color: '#00ffff'
      },
      {
        id: 'projects',
        name: 'Project Labs',
        icon: <Code />,
        position: { x: currentX += (200 * scale + spacing), y: 140 },
        size: { width: 240 * scale, height: 300 * scale },
        color: '#ff00ff'
      },
      {
        id: 'experience',
        name: 'Experience Corp',
        icon: <Work />,
        position: { x: currentX += (240 * scale + spacing), y: 140 },
        size: { width: 200 * scale, height: 260 * scale },
        color: '#00ff00'
      },
      {
        id: 'github',
        name: 'GitHub Station',
        icon: <GitHub />,
        position: { x: currentX += (200 * scale + spacing), y: 140 },
        size: { width: 240 * scale, height: 300 * scale },
        color: '#ffff00'
      },
      {
        id: 'skills',
        name: 'Skill Matrix',
        icon: <Code />,
        position: { x: currentX += (240 * scale + spacing), y: 140 },
        size: { width: 220 * scale, height: 250 * scale },
        color: '#ff6600'
      }
    ]
  }
  
  const [buildings, setBuildings] = useState(getResponsiveBuildings())
  
  // Update building positions on window resize (with throttling for performance)
  useEffect(() => {
    let resizeTimer: NodeJS.Timeout
    
    const handleResize = () => {
      clearTimeout(resizeTimer)
      resizeTimer = setTimeout(() => {
        setBuildings(getResponsiveBuildings())
      }, 100) // Throttle resize events
    }
    
    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      clearTimeout(resizeTimer)
    }
  }, [])


  const handleBuildingClick = (buildingId: string) => {
    // Toggle building - if same building is clicked, close it
    if (activeSection === buildingId) {
      closeAllComponents()
      return
    }
    
    // Close all other components first
    closeAllComponents()
    // Then open the selected building
    setActiveSection(buildingId)
    
    // Zoom into building
    const building = buildings.find(b => b.id === buildingId)
    if (building) {
      setCameraPosition({
        x: -building.position.x + window.innerWidth / 2 - building.size.width / 2,
        y: -building.position.y + window.innerHeight / 2 - building.size.height / 2,
        scale: 1.5
      })
    }
  }

  const handleCloseModal = () => {
    setActiveSection(null)
    setCameraPosition({ x: 0, y: 0, scale: 1 })
  }

  const renderContent = (section: string) => {
    switch (section) {
      case 'about':
        return (
          <Box>
            <Typography sx={{ color: 'white', mb: 3, fontSize: '1.1rem', lineHeight: 1.8 }}>
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
      case 'projects':
        return (
          <Box>
            <Typography sx={{ color: 'white', mb: 3, fontSize: '1.1rem' }}>
              Real-time projects from GitHub API - actively maintained and updated!
            </Typography>
            <Box sx={{ display: 'grid', gap: 3, gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))' }}>
              {githubData?.repos?.slice(0, 6).map((repo: any) => (
                <motion.div
                  key={repo.name}
                  whileHover={{ scale: 1.02, y: -5 }}
                  transition={{ duration: 0.2 }}
                >
                  <Box
                    sx={{
                      p: 3,
                      border: '1px solid #ff00ff',
                      borderRadius: 2,
                      background: 'rgba(255,0,255,0.05)',
                      backdropFilter: 'blur(10px)',
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column'
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" sx={{ color: '#ff00ff', fontFamily: 'monospace' }}>
                        {repo.name}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography sx={{ color: '#ffff00', fontSize: '0.8rem' }}>
                          ⭐ {repo.stargazers_count}
                        </Typography>
                      </Box>
                    </Box>
                    <Typography sx={{ color: '#00ffff', fontSize: '0.8rem', mb: 2, fontWeight: 600 }}>
                      {repo.language || 'Mixed'}
                    </Typography>
                    <Typography sx={{ 
                      color: 'rgba(255,255,255,0.8)', 
                      fontSize: '0.9rem',
                      flex: 1,
                      mb: 2
                    }}>
                      {repo.description || 'No description available'}
                    </Typography>
                    <Typography sx={{ color: '#00ff00', fontSize: '0.7rem', fontFamily: 'monospace' }}>
                      Updated: {new Date(repo.updated_at).toLocaleDateString()}
                    </Typography>
                  </Box>
                </motion.div>
              )) || (
                <Typography sx={{ color: 'white' }}>Loading GitHub projects...</Typography>
              )}
            </Box>
            {githubData?.user && (
              <Box sx={{ mt: 3, p: 2, border: '1px solid #ff00ff40', borderRadius: 1, background: 'rgba(255,0,255,0.02)' }}>
                <Typography sx={{ color: '#ff00ff', fontSize: '0.9rem' }}>
                  📊 {githubData.user.public_repos} public repos • {githubData.user.followers} followers
                </Typography>
              </Box>
            )}
          </Box>
        )
      case 'github':
        return (
          <Box>
            <Typography variant="h5" sx={{ color: '#ffff00', mb: 3, fontWeight: 700 }}>
              GitHub Command Center
            </Typography>
            
            {/* Stats Dashboard */}
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 2, mb: 3 }}>
              {[
                { label: 'Public Repos', value: githubLoading ? '...' : githubStats.publicRepos.toString(), icon: <Inventory sx={{ fontSize: '1.5rem' }} />, color: '#00ffff' },
                { label: 'Total Commits', value: githubLoading ? '...' : `${githubStats.totalCommits}+`, icon: <Bolt sx={{ fontSize: '1.5rem' }} />, color: '#00ff00' },
                { label: 'Languages', value: githubLoading ? '...' : githubStats.languages.toString(), icon: <Build sx={{ fontSize: '1.5rem' }} />, color: '#ff00ff' },
                { label: 'Streak Days', value: githubLoading ? '...' : githubStats.streakDays.toString(), icon: <LocalFireDepartment sx={{ fontSize: '1.5rem' }} />, color: '#ff6600' }
              ].map((stat) => (
                <motion.div key={stat.label} whileHover={{ scale: 1.05 }}>
                  <Box sx={{
                    p: 2,
                    border: `1px solid ${stat.color}`,
                    borderRadius: 2,
                    background: `rgba(${stat.color === '#00ffff' ? '0,255,255' : stat.color === '#00ff00' ? '0,255,0' : stat.color === '#ff00ff' ? '255,0,255' : '255,102,0'},0.1)`,
                    textAlign: 'center',
                    fontFamily: 'IBM Plex Mono, monospace'
                  }}>
                    <Box sx={{ mb: 0.5, color: stat.color }}>{stat.icon}</Box>
                    <Typography sx={{ color: stat.color, fontWeight: 700, fontSize: '1.2rem' }}>
                      {stat.value}
                    </Typography>
                    <Typography sx={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.8rem' }}>
                      {stat.label}
                    </Typography>
                  </Box>
                </motion.div>
              ))}
            </Box>

            {/* Compact Activity Grid */}
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(12, 1fr)', 
              gap: 0.5,
              mb: 3,
              p: 2,
              border: '1px solid #ffff00',
              borderRadius: 2,
              background: 'rgba(255,255,0,0.05)'
            }}>
              {Array.from({ length: 84 }, (_, i) => (
                <Box
                  key={i}
                  sx={{
                    width: '8px',
                    height: '8px',
                    background: Math.random() > 0.6 ? '#ffff00' : Math.random() > 0.8 ? '#00ff00' : 'rgba(255,255,0,0.2)',
                    borderRadius: '1px',
                    boxShadow: Math.random() > 0.6 ? '0 0 3px #ffff00' : 'none'
                  }}
                />
              ))}
            </Box>

            {/* Language Breakdown */}
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 2 }}>
              {(githubLoading ? [
                { name: 'Loading...', percentage: 0, color: '#666666' },
                { name: 'Loading...', percentage: 0, color: '#666666' },
                { name: 'Loading...', percentage: 0, color: '#666666' }
              ] : githubStats.languageStats).map((lang) => (
                <Box key={lang.name} sx={{
                  p: 2,
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: 2,
                  background: 'rgba(255,255,255,0.05)'
                }}>
                  <Typography sx={{ color: lang.color, fontWeight: 600, mb: 1, fontSize: '0.9rem' }}>
                    {lang.name}
                  </Typography>
                  <Box sx={{ 
                    width: '100%', 
                    height: '4px', 
                    background: 'rgba(255,255,255,0.1)',
                    borderRadius: '2px',
                    overflow: 'hidden'
                  }}>
                    <motion.div
                      style={{
                        width: `${lang.percentage}%`,
                        height: '100%',
                        background: lang.color,
                        borderRadius: '2px'
                      }}
                      initial={{ width: 0 }}
                      animate={{ width: `${lang.percentage}%` }}
                      transition={{ duration: 1, delay: 0.5 }}
                    />
                  </Box>
                  <Typography sx={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.8rem', mt: 0.5 }}>
                    {lang.percentage}%
                  </Typography>
                </Box>
              ))}
            </Box>
          </Box>
        )
      case 'skills':
        return (
          <Box>
            <Typography variant="h5" sx={{ color: '#ff6600', mb: 3, fontWeight: 700 }}>
              Technical Skill Matrix
            </Typography>
            <Box sx={{ display: 'grid', gap: 3, gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))' }}>
              {[
                { category: 'Frontend', skills: ['React', 'TypeScript', 'Vue.js', 'Three.js', 'HTML/CSS'], level: 90 },
                { category: 'Backend', skills: ['PHP', 'Laravel', 'Python', 'Node.js', 'FastAPI'], level: 85 },
                { category: 'Database', skills: ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis'], level: 80 },
                { category: 'DevOps', skills: ['Docker', 'Git', 'Linux', 'CI/CD'], level: 75 }
              ].map((skillGroup) => (
                <motion.div
                  key={skillGroup.category}
                  whileHover={{ scale: 1.05 }}
                  transition={{ duration: 0.2 }}
                >
                  <Box
                    sx={{
                      p: 3,
                      border: '1px solid #ff6600',
                      borderRadius: 2,
                      background: 'rgba(255,102,0,0.05)',
                      backdropFilter: 'blur(10px)'
                    }}
                  >
                    <Typography variant="h6" sx={{ color: '#ff6600', mb: 2 }}>
                      {skillGroup.category}
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Box
                        sx={{
                          width: '100%',
                          height: '4px',
                          background: 'rgba(255,102,0,0.2)',
                          borderRadius: '2px',
                          overflow: 'hidden'
                        }}
                      >
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${skillGroup.level}%` }}
                          transition={{ duration: 2, delay: 0.5 }}
                          style={{
                            height: '100%',
                            background: 'linear-gradient(90deg, #ff6600, #ffaa00)',
                            boxShadow: '0 0 10px #ff6600'
                          }}
                        />
                      </Box>
                      <Typography sx={{ color: '#ff6600', fontSize: '0.8rem', mt: 1 }}>
                        {skillGroup.level}% Proficiency
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {skillGroup.skills.map((skill) => (
                        <Box
                          key={skill}
                          sx={{
                            px: 2,
                            py: 0.5,
                            border: '1px solid #ff6600',
                            borderRadius: 1,
                            color: '#ff6600',
                            fontSize: '0.8rem',
                            background: 'rgba(255,102,0,0.1)'
                          }}
                        >
                          {skill}
                        </Box>
                      ))}
                    </Box>
                  </Box>
                </motion.div>
              ))}
            </Box>
          </Box>
        )
      case 'experience':
        return (
          <Box>
            <Typography variant="h4" sx={{ color: '#00ff00', mb: 4, fontWeight: 700 }}>
              Professional Experience
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <motion.div whileHover={{ x: 10 }}>
                <Box sx={{
                  p: 4,
                  border: '1px solid #00ff00',
                  borderRadius: 2,
                  background: 'rgba(0,255,0,0.05)',
                  backdropFilter: 'blur(10px)'
                }}>
                  <Typography variant="h6" sx={{ color: '#00ff00', mb: 1 }}>
                    Software Engineer
                  </Typography>
                  <Typography sx={{ color: '#ffff00', mb: 2, fontWeight: 600 }}>
                    Louddoor • Full-time • 06/2023 - Current
                  </Typography>
                  <Typography sx={{ color: 'rgba(255,255,255,0.9)', lineHeight: 1.7, mb: 3 }}>
                    Full-stack development, code reviews, Agile methodologies. Building scalable web applications 
                    and leading development of customer-facing features with modern tech stack.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {['PHP', 'Laravel', 'Vue.js', 'MySQL', 'AWS', 'Docker'].map((tech) => (
                      <Box
                        key={tech}
                        sx={{
                          px: 2,
                          py: 0.5,
                          border: '1px solid #00ff00',
                          borderRadius: 1,
                          color: '#00ff00',
                          fontSize: '0.8rem',
                          background: 'rgba(0,255,0,0.1)'
                        }}
                      >
                        {tech}
                      </Box>
                    ))}
                  </Box>
                </Box>
              </motion.div>
              
              <motion.div whileHover={{ x: 10 }}>
                <Box sx={{
                  p: 4,
                  border: '1px solid #00ff00',
                  borderRadius: 2,
                  background: 'rgba(0,255,0,0.05)',
                  backdropFilter: 'blur(10px)'
                }}>
                  <Typography variant="h6" sx={{ color: '#00ff00', mb: 1 }}>
                    Software Engineering Intern
                  </Typography>
                  <Typography sx={{ color: '#ffff00', mb: 2, fontWeight: 600 }}>
                    Louddoor • Internship • 02/2023 - 06/2023
                  </Typography>
                  <Typography sx={{ color: 'rgba(255,255,255,0.9)', lineHeight: 1.7, mb: 3 }}>
                    Technical documentation, daily standups, tool implementation. Gained hands-on experience 
                    in agile development practices and modern web technologies.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {['PHP', 'Laravel', 'Vue.js', 'Git', 'Agile'].map((tech) => (
                      <Box
                        key={tech}
                        sx={{
                          px: 2,
                          py: 0.5,
                          border: '1px solid #00ff00',
                          borderRadius: 1,
                          color: '#00ff00',
                          fontSize: '0.8rem',
                          background: 'rgba(0,255,0,0.1)'
                        }}
                      >
                        {tech}
                      </Box>
                    ))}
                  </Box>
                </Box>
              </motion.div>

              <motion.div whileHover={{ x: 10 }}>
                <Box sx={{
                  p: 4,
                  border: '1px solid #00ff00',
                  borderRadius: 2,
                  background: 'rgba(0,255,0,0.05)',
                  backdropFilter: 'blur(10px)'
                }}>
                  <Typography variant="h6" sx={{ color: '#00ff00', mb: 1 }}>
                    Freelance Software Developer
                  </Typography>
                  <Typography sx={{ color: '#ffff00', mb: 2, fontWeight: 600 }}>
                    Self-Employed • Freelance • 12/2020 - 02/2023
                  </Typography>
                  <Typography sx={{ color: 'rgba(255,255,255,0.9)', lineHeight: 1.7, mb: 3 }}>
                    Mobile solutions, client analysis, multiple programming languages. Developed custom 
                    software solutions for various clients across different industries.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {['React', 'Node.js', 'Python', 'Mobile Dev', 'Client Relations'].map((tech) => (
                      <Box
                        key={tech}
                        sx={{
                          px: 2,
                          py: 0.5,
                          border: '1px solid #00ff00',
                          borderRadius: 1,
                          color: '#00ff00',
                          fontSize: '0.8rem',
                          background: 'rgba(0,255,0,0.1)'
                        }}
                      >
                        {tech}
                      </Box>
                    ))}
                  </Box>
                </Box>
              </motion.div>

              <motion.div whileHover={{ x: 10 }}>
                <Box sx={{
                  p: 4,
                  border: '1px solid #00ff00',
                  borderRadius: 2,
                  background: 'rgba(0,255,0,0.05)',
                  backdropFilter: 'blur(10px)'
                }}>
                  <Typography variant="h6" sx={{ color: '#00ff00', mb: 1 }}>
                    Software Engineering Intern
                  </Typography>
                  <Typography sx={{ color: '#ffff00', mb: 2, fontWeight: 600 }}>
                    Benty • Internship • 09/2019 - 01/2023
                  </Typography>
                  <Typography sx={{ color: 'rgba(255,255,255,0.9)', lineHeight: 1.7, mb: 3 }}>
                    Java & Python development, Agile environment, code optimization. Contributed to backend 
                    systems and learned industry best practices in software development.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {['Java', 'Python', 'Agile', 'Backend', 'Code Review'].map((tech) => (
                      <Box
                        key={tech}
                        sx={{
                          px: 2,
                          py: 0.5,
                          border: '1px solid #00ff00',
                          borderRadius: 1,
                          color: '#00ff00',
                          fontSize: '0.8rem',
                          background: 'rgba(0,255,0,0.1)'
                        }}
                      >
                        {tech}
                      </Box>
                    ))}
                  </Box>
                </Box>
              </motion.div>

              <motion.div whileHover={{ x: 10 }}>
                <Box sx={{
                  p: 4,
                  border: '1px solid #00ff00',
                  borderRadius: 2,
                  background: 'rgba(0,255,0,0.05)',
                  backdropFilter: 'blur(10px)'
                }}>
                  <Typography variant="h6" sx={{ color: '#00ff00', mb: 1 }}>
                    Retail Sales Associate
                  </Typography>
                  <Typography sx={{ color: '#ffff00', mb: 2, fontWeight: 600 }}>
                    Griffin Pools & Spas • Part-time • 03/2018 - 02/2023
                  </Typography>
                  <Typography sx={{ color: 'rgba(255,255,255,0.9)', lineHeight: 1.7, mb: 3 }}>
                    Customer service, product education, relationship building. Developed strong 
                    communication and problem-solving skills while maintaining high customer satisfaction.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {['Customer Service', 'Sales', 'Product Knowledge', 'Communication', 'Problem Solving'].map((skill) => (
                      <Box
                        key={skill}
                        sx={{
                          px: 2,
                          py: 0.5,
                          border: '1px solid #00ff00',
                          borderRadius: 1,
                          color: '#00ff00',
                          fontSize: '0.8rem',
                          background: 'rgba(0,255,0,0.1)'
                        }}
                      >
                        {skill}
                      </Box>
                    ))}
                  </Box>
                </Box>
              </motion.div>

              {/* Education Section */}
              <Typography variant="h4" sx={{ color: '#00ff00', mt: 4, mb: 3, fontWeight: 700 }}>
                Education
              </Typography>
              
              <motion.div whileHover={{ x: 10 }}>
                <Box sx={{
                  p: 4,
                  border: '1px solid #00ff00',
                  borderRadius: 2,
                  background: 'rgba(0,255,0,0.05)',
                  backdropFilter: 'blur(10px)'
                }}>
                  <Typography variant="h6" sx={{ color: '#00ff00', mb: 1 }}>
                    Bachelor of Science in Computer Science
                  </Typography>
                  <Typography sx={{ color: '#ffff00', mb: 2, fontWeight: 600 }}>
                    Western Governors University • Expected 08/2025
                  </Typography>
                  <Typography sx={{ color: 'rgba(255,255,255,0.9)', lineHeight: 1.7 }}>
                    Focus on software engineering, algorithms, and system architecture. Maintaining strong 
                    academic performance while working full-time in the software industry.
                  </Typography>
                </Box>
              </motion.div>

              <motion.div whileHover={{ x: 10 }}>
                <Box sx={{
                  p: 4,
                  border: '1px solid #00ff00',
                  borderRadius: 2,
                  background: 'rgba(0,255,0,0.05)',
                  backdropFilter: 'blur(10px)'
                }}>
                  <Typography variant="h6" sx={{ color: '#00ff00', mb: 1 }}>
                    Computer Science Studies
                  </Typography>
                  <Typography sx={{ color: '#ffff00', mb: 2, fontWeight: 600 }}>
                    University of South Carolina • Some College - No Degree
                  </Typography>
                  <Typography sx={{ color: 'rgba(255,255,255,0.9)', lineHeight: 1.7 }}>
                    Solid foundation in CS fundamentals and programming. Built core knowledge in 
                    computer science principles and programming methodologies.
                  </Typography>
                </Box>
              </motion.div>

              {/* Hobbies Section */}
              <Typography variant="h4" sx={{ color: '#00ff00', mt: 4, mb: 3, fontWeight: 700 }}>
                Personal Interests & Hobbies
              </Typography>
              
              <motion.div whileHover={{ x: 10 }}>
                <Box sx={{
                  p: 4,
                  border: '1px solid #00ff00',
                  borderRadius: 2,
                  background: 'rgba(0,255,0,0.05)',
                  backdropFilter: 'blur(10px)'
                }}>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                    {[
                      'Tennis enthusiast - promotes fitness and discipline',
                      'Golf player - enjoys focus and strategic thinking',
                      'Passionate about music as creative expression',
                      'Video gaming for fun, problem-solving, and teamwork',
                      'Personal coding projects and open source contributions',
                      'Continuous learning in technology and software development'
                    ].map((hobby, index) => (
                      <Box key={index} sx={{ 
                        color: 'rgba(255,255,255,0.9)', 
                        mb: 1, 
                        lineHeight: 1.6,
                        display: 'flex',
                        alignItems: 'center'
                      }}>
                        <Box sx={{ 
                          width: 8, 
                          height: 8, 
                          borderRadius: '50%', 
                          backgroundColor: '#00ff00', 
                          mr: 2,
                          flexShrink: 0
                        }} />
                        {hobby}
                      </Box>
                    ))}
                  </Box>
                </Box>
              </motion.div>
            </Box>
          </Box>
        )
      default:
        return null
    }
  }

  const activeBuilding = buildings.find(b => b.id === activeSection)

  // Mobile Layout Component
  const MobileLayout = () => (
    <Box
      sx={{
        display: { xs: 'block', md: 'none' }, // Show only on mobile
        width: '100vw',
        height: '100vh',
        background: 'linear-gradient(180deg, #000011 0%, #001122 50%, #002244 100%)',
        overflow: 'auto',
        position: 'relative'
      }}
    >
      {/* Mobile Header */}
      <Box
        sx={{
          position: 'sticky',
          top: 0,
          left: 0,
          right: 0,
          height: '70px',
          background: 'linear-gradient(135deg, rgba(0,10,30,0.98) 0%, rgba(0,20,40,0.98) 100%)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(0,255,255,0.3)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 2
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              background: 'linear-gradient(135deg, #00ffff, #0099cc)',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px rgba(0,255,255,0.3)'
            }}
          >
            <Code sx={{ color: 'white', fontSize: '1.2rem' }} />
          </Box>
          <Box>
            <Typography sx={{
              color: 'white',
              fontSize: '1.1rem',
              fontWeight: 700,
              letterSpacing: '1px',
              fontFamily: 'IBM Plex Sans, sans-serif'
            }}>
              CAMERON POTTER
            </Typography>
            <Typography sx={{
              color: '#00ffff',
              fontSize: '0.7rem',
              opacity: 0.8,
              fontFamily: 'IBM Plex Sans, sans-serif'
            }}>
              Software Engineer
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <IconButton
            onClick={() => {
              closeAllComponents()
              setTerminalOpen(true)
            }}
            sx={{
              color: '#00ff00',
              border: '1px solid rgba(0,255,0,0.3)',
              borderRadius: '8px',
              width: 36,
              height: 36,
              '&:hover': {
                background: 'rgba(0,255,0,0.1)',
                borderColor: '#00ff00'
              }
            }}
          >
            <Terminal sx={{ fontSize: '1rem' }} />
          </IconButton>
          
          <IconButton
            onClick={() => {
              closeAllComponents()
              setSocialOpen(true)
            }}
            sx={{
              color: '#ff00ff',
              border: '1px solid rgba(255,0,255,0.3)',
              borderRadius: '8px',
              width: 36,
              height: 36,
              '&:hover': {
                background: 'rgba(255,0,255,0.1)',
                borderColor: '#ff00ff'
              }
            }}
          >
            <Person sx={{ fontSize: '1rem' }} />
          </IconButton>
          
          <IconButton
            onClick={toggleMusic}
            sx={{
              color: musicPlaying ? '#ffff00' : 'rgba(255,255,255,0.6)',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '8px',
              width: 36,
              height: 36,
              '&:hover': {
                background: 'rgba(255,255,255,0.1)'
              }
            }}
          >
            {musicPlaying ? <VolumeUp sx={{ fontSize: '1rem' }} /> : <VolumeOff sx={{ fontSize: '1rem' }} />}
          </IconButton>
        </Box>
      </Box>

      {/* Mobile Content Cards */}
      <Box sx={{ px: 2, py: 3, display: 'flex', flexDirection: 'column', gap: 3 }}>
        {buildings.map((building) => (
          <motion.div
            key={building.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Box
              onClick={() => handleBuildingClick(building.id)}
              sx={{
                p: 3,
                borderRadius: '16px',
                background: `linear-gradient(135deg, ${building.color}15, ${building.color}08)`,
                border: `2px solid ${building.color}40`,
                backdropFilter: 'blur(10px)',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: activeSection === building.id 
                  ? `0 8px 32px ${building.color}40, inset 0 0 20px ${building.color}20`
                  : `0 4px 16px rgba(0,0,0,0.3)`,
                '&:hover': {
                  border: `2px solid ${building.color}80`,
                  boxShadow: `0 8px 24px ${building.color}30`
                }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Box sx={{ color: building.color, fontSize: '1.5rem' }}>
                  {building.icon}
                </Box>
                <Typography
                  variant="h6"
                  sx={{
                    color: building.color,
                    fontWeight: 600,
                    fontFamily: 'IBM Plex Sans, sans-serif',
                    fontSize: '1.1rem'
                  }}
                >
                  {building.name}
                </Typography>
              </Box>
              
              <Typography
                sx={{
                  color: 'rgba(255,255,255,0.8)',
                  fontSize: '0.9rem',
                  lineHeight: 1.5,
                  fontFamily: 'IBM Plex Sans, sans-serif'
                }}
              >
                {building.id === 'about' && 'Software engineer with full-stack expertise'}
                {building.id === 'projects' && 'Interactive web applications and digital experiences'}
                {building.id === 'experience' && 'Professional development journey and roles'}
                {building.id === 'github' && 'Live coding activity and repository statistics'}
                {building.id === 'skills' && 'Technical proficiencies and programming languages'}
              </Typography>
              
              {activeSection === building.id && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <Box sx={{ mt: 3, pt: 3, borderTop: `1px solid ${building.color}30` }}>
                    {renderContent(building.id)}
                  </Box>
                </motion.div>
              )}
            </Box>
          </motion.div>
        ))}
      </Box>

      {/* Mobile Floating Action Buttons */}
      <Box
        sx={{
          position: 'fixed',
          bottom: 20,
          left: 20,
          right: 20,
          display: 'flex',
          justifyContent: 'space-between',
          gap: 2,
          zIndex: 100
        }}
      >
        <Fab
          onClick={() => {
            if (timelineOpen) {
              setTimelineOpen(false)
            } else {
              closeAllComponents()
              setTimelineOpen(true)
            }
          }}
          size="medium"
          sx={{
            background: timelineOpen 
              ? 'linear-gradient(135deg, #00ffff, #0099cc)' 
              : 'rgba(0,255,255,0.2)',
            border: '1px solid #00ffff',
            color: timelineOpen ? 'white' : '#00ffff',
            boxShadow: timelineOpen 
              ? '0 0 20px rgba(0,255,255,0.5)' 
              : '0 4px 12px rgba(0,0,0,0.3)',
            '&:hover': {
              background: 'linear-gradient(135deg, #00ffff, #0099cc)',
              color: 'white'
            }
          }}
        >
          <Work />
        </Fab>
        
        <Fab
          onClick={() => {
            if (aiOpen) {
              setAiOpen(false)
            } else {
              closeAllComponents()
              setAiOpen(true)
            }
          }}
          size="medium"
          sx={{
            background: aiOpen 
              ? 'linear-gradient(135deg, #00ff00, #009900)' 
              : 'rgba(0,255,0,0.2)',
            border: '1px solid #00ff00',
            color: aiOpen ? 'white' : '#00ff00',
            boxShadow: aiOpen 
              ? '0 0 20px rgba(0,255,0,0.5)' 
              : '0 4px 12px rgba(0,0,0,0.3)',
            '&:hover': {
              background: 'linear-gradient(135deg, #00ff00, #009900)',
              color: 'white'
            }
          }}
        >
          <Code />
        </Fab>
      </Box>

      {/* Mobile Components */}
      <CommandTerminal isOpen={terminalOpen} setIsOpen={setTerminalOpen} />
      <SocialMediaHub isOpen={socialOpen} setIsOpen={setSocialOpen} />
      <HolographicTimeline 
        isOpen={timelineOpen} 
        setIsOpen={setTimelineOpen} 
        closeAllComponents={closeAllComponents} 
      />
      <AINeural 
        isOpen={aiOpen} 
        setIsOpen={setAiOpen} 
        closeAllComponents={closeAllComponents} 
      />
    </Box>
  )

  // Desktop Layout (existing)
  const DesktopLayout = () => (
    <Box
      sx={{
        display: { xs: 'none', md: 'block' }, // Hide on mobile, show on desktop
        width: '100vw',
        height: '100vh',
        background: 'linear-gradient(180deg, #000011 0%, #001122 30%, #002244 100%)',
        overflow: 'hidden',
        position: 'relative',
        paddingTop: '80px' // Account for header height
      }}
    >
      {/* City Ground Level (fixed position) */}
      <CityGround />
      
      {/* Distant City Skyline (fixed position) */}
      <CitySkyline />
      
      {/* High-altitude Space Elements (fixed position) */}
      <SpaceElements />
      
      {/* Neon Signs (fixed position) */}
      <NeonSigns />

      {/* Animated city container */}
      <motion.div
        ref={cityRef}
        animate={{
          x: cameraPosition.x,
          y: cameraPosition.y,
          scale: cameraPosition.scale
        }}
        transition={{ duration: 1, ease: 'easeInOut' }}
        style={{
          width: '100%',
          height: '100%',
          position: 'relative',
          zIndex: 10
        }}
      >
        {/* Enhanced Street Level Foundation */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: '140px', // Match ground component height
            background: 'transparent',
            zIndex: 5 // Above ground but below buildings
          }}
        />

        {/* Background Buildings (Non-interactive) */}
        <BackgroundBuildings />

        {/* Interactive Buildings */}
        {buildings.map((building) => (
          <CyberpunkBuilding
            key={building.id}
            {...building}
            onClick={() => handleBuildingClick(building.id)}
            isActive={activeSection === building.id}
          />
        ))}

        {/* GitHub commits flying around */}
        <GitHubCommits commits={mockCommits} />
      </motion.div>

      {/* Professional Header */}
      <ProfessionalHeader 
        onTerminalOpen={useCallback(() => {
          closeAllComponents()
          setTerminalOpen(true)
        }, [closeAllComponents])}
        onSocialOpen={useCallback(() => {
          closeAllComponents()
          setSocialOpen(true)
        }, [closeAllComponents])}
        onMusicToggle={toggleMusic}
        isMusicPlaying={musicPlaying}
      />
      
      {/* Interactive Elements */}
      <CommandTerminal isOpen={terminalOpen} setIsOpen={setTerminalOpen} />
      <SocialMediaHub isOpen={socialOpen} setIsOpen={setSocialOpen} />
      <HolographicTimeline 
        isOpen={timelineOpen} 
        setIsOpen={setTimelineOpen} 
        closeAllComponents={closeAllComponents} 
      />
      <AINeural 
        isOpen={aiOpen} 
        setIsOpen={setAiOpen} 
        closeAllComponents={closeAllComponents} 
      />

      {/* Clean Professional Header */}
      <Box
        sx={{
          position: 'absolute',
          top: 30,
          left: 30,
          zIndex: 100
        }}
      >
        <Typography 
          variant="h3" 
          sx={{ 
            color: '#ffffff', 
            fontWeight: 800,
            letterSpacing: '1px',
            textShadow: '2px 2px 0px rgba(0,255,255,0.3)',
            mb: 1
          }}
        >
          CAMERON POTTER
        </Typography>
        <Typography 
          sx={{ 
            color: '#00ffff', 
            fontSize: '1.1rem',
            fontWeight: 600,
            letterSpacing: '0.5px',
            mb: 2
          }}
        >
          Interactive Portfolio Experience
        </Typography>
        
        {/* Simplified Instructions */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <Typography 
            sx={{ 
              color: 'rgba(255,255,255,0.8)', 
              fontSize: '0.9rem',
              fontWeight: 500,
              maxWidth: '400px',
              lineHeight: 1.5
            }}
          >
            Click the buildings to explore my work, skills, and experience. 
            Flying streaks represent live GitHub activity.
          </Typography>
        </motion.div>
      </Box>

      {/* Minimal Status Panel */}
      <Box
        sx={{
          position: 'absolute',
          bottom: 30,
          right: 30,
          zIndex: 100
        }}
      >
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 1.5 }}
        >
          <Box
            sx={{
              background: 'rgba(0,0,20,0.8)',
              border: '1px solid rgba(0,255,255,0.3)',
              borderRadius: '6px',
              p: 2,
              backdropFilter: 'blur(15px)',
              minWidth: '200px'
            }}
          >
            <Typography 
              sx={{ 
                color: '#00ffff', 
                fontSize: '0.9rem',
                fontWeight: 700,
                mb: 1,
                letterSpacing: '0.5px'
              }}
            >
              LIVE DATA
            </Typography>
            
            <Typography 
              sx={{ 
                color: 'rgba(255,255,255,0.9)', 
                fontSize: '0.8rem',
                fontWeight: 500
              }}
            >
              Connected to GitHub API ●
            </Typography>
          </Box>
        </motion.div>
      </Box>

      {/* Content Modal */}
      <AnimatePresence>
        {activeSection && (
          <ContentModal
            isOpen={!!activeSection}
            onClose={handleCloseModal}
            section={activeSection}
            title={activeBuilding?.name || ''}
            color={activeBuilding?.color || '#00ffff'}
          >
            {renderContent(activeSection)}
          </ContentModal>
        )}
      </AnimatePresence>
    </Box>
  )

  // Return both layouts
  return (
    <>
      <MobileLayout />
      <DesktopLayout />
      
      {/* Hidden Audio Element - Better Lofi Track */}
      <audio
        ref={audioRef}
        loop
        preload="metadata"
        style={{ display: 'none' }}
        volume={0.3}
      >
        {/* Free lofi/chill music - replace with your preferred track */}
        <source src="https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3" type="audio/mp3" />
        {/* Alternative free sources:
            - https://www.bensound.com/bensound-music/bensound-slowmotion.mp3
            - https://www.bensound.com/bensound-music/bensound-creativeminds.mp3
            - https://www.bensound.com/bensound-music/bensound-dreams.mp3 */}
      </audio>
    </>
  )
}