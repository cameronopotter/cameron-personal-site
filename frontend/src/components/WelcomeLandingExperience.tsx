import React, { useState, useEffect, useRef } from 'react'
import { 
  Box, 
  Typography, 
  Button, 
  Card, 
  CardContent, 
  Fade, 
  Grow,
  LinearProgress,
  Chip,
  IconButton,
  Backdrop
} from '@mui/material'
import { 
  PlayArrow as PlayIcon,
  Skip as SkipIcon,
  VolumeOff as MuteIcon,
  VolumeUp as UnmuteIcon,
  Fullscreen as FullscreenIcon,
  Close as CloseIcon,
  GitHub as GitHubIcon,
  Work as WorkIcon,
  Code as CodeIcon,
  School as SchoolIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'
import { useSpring, animated } from 'react-spring'

interface WelcomeLandingExperienceProps {
  onComplete: () => void
  onSkip: () => void
}

interface WelcomeStep {
  id: string
  title: string
  subtitle: string
  description: string
  animation: string
  duration: number
  actions?: Array<{
    label: string
    action: () => void
    primary?: boolean
  }>
}

const welcomeSteps: WelcomeStep[] = [
  {
    id: 'intro',
    title: "Welcome to Cameron's Digital Greenhouse",
    subtitle: "Where Code Grows into Innovation",
    description: "Experience my portfolio as a living, breathing 3D garden where each project is a unique plant that grows based on real development activity and engagement.",
    animation: 'fadeUp',
    duration: 4000
  },
  {
    id: 'concept',
    title: "The Garden Concept",
    subtitle: "Projects as Living Organisms",
    description: "Each plant represents a different project, growing taller and more complex as it receives commits, stars, and interaction. Watch as seasons change and weather systems reflect the current state of development.",
    animation: 'slideRight',
    duration: 5000
  },
  {
    id: 'interaction',
    title: "Interactive Exploration",
    subtitle: "Click, Explore, Discover",
    description: "Click on plants to learn about projects, hover over constellations to see skills, and navigate through different seasons. The garden responds to your presence and curiosity.",
    animation: 'fadeIn',
    duration: 4000
  },
  {
    id: 'developer',
    title: "About the Developer",
    subtitle: "Cameron Potter - Full-Stack Engineer",
    description: "Currently crafting scalable solutions at Louddoor using PHP, Laravel, and Vue.js. Pursuing Computer Science at Western Governors University with a passion for clean code and innovative user experiences.",
    animation: 'slideLeft',
    duration: 5000,
    actions: [
      {
        label: 'View GitHub',
        action: () => window.open('https://github.com/cameronopotter', '_blank')
      },
      {
        label: 'Contact Me',
        action: () => window.open('mailto:cameronopotter@gmail.com')
      }
    ]
  },
  {
    id: 'ready',
    title: "Ready to Explore?",
    subtitle: "Your Journey Through the Digital Greenhouse Begins",
    description: "Take your time to wander through the garden, discover projects, learn about technologies, and see how creativity and code merge into something beautiful.",
    animation: 'scaleUp',
    duration: 3000,
    actions: [
      {
        label: 'Enter Garden',
        action: () => {},
        primary: true
      }
    ]
  }
]

// Loading Animation Component
const LoadingSequence: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const [progress, setProgress] = useState(0)
  const [loadingText, setLoadingText] = useState('Planting seeds...')
  
  const loadingSteps = [
    'Planting seeds...',
    'Watering the soil...',
    'Growing plants...',
    'Adding sunshine...',
    'Creating atmosphere...',
    'Preparing your garden...'
  ]
  
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev + 2
        const stepIndex = Math.floor((newProgress / 100) * loadingSteps.length)
        setLoadingText(loadingSteps[Math.min(stepIndex, loadingSteps.length - 1)])
        
        if (newProgress >= 100) {
          clearInterval(interval)
          setTimeout(onComplete, 500)
        }
        
        return newProgress
      })
    }, 50)
    
    return () => clearInterval(interval)
  }, [onComplete, loadingSteps])
  
  return (
    <Box
      sx={{
        position: 'fixed',
        inset: 0,
        bgcolor: 'rgba(10, 10, 10, 0.98)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999
      }}
    >
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 260, damping: 20 }}
      >
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h3" color="#4CAF50" fontWeight="bold" mb={2}>
            🌱 Digital Greenhouse
          </Typography>
          <Typography variant="h6" color="white" mb={4}>
            Cameron Potter's Interactive Portfolio
          </Typography>
          
          <Box sx={{ width: 300, mb: 2 }}>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 8,
                borderRadius: 4,
                bgcolor: 'rgba(76, 175, 80, 0.2)',
                '& .MuiLinearProgress-bar': {
                  bgcolor: '#4CAF50',
                  borderRadius: 4
                }
              }}
            />
          </Box>
          
          <Typography variant="body1" color="rgba(255,255,255,0.7)">
            {loadingText}
          </Typography>
          <Typography variant="body2" color="rgba(255,255,255,0.5)" mt={1}>
            {progress}%
          </Typography>
        </Box>
      </motion.div>
    </Box>
  )
}

// Individual Step Component
const WelcomeStepCard: React.FC<{
  step: WelcomeStep
  isActive: boolean
  onAction: (action: () => void) => void
}> = ({ step, isActive, onAction }) => {
  
  const getAnimationVariants = () => {
    switch (step.animation) {
      case 'fadeUp':
        return {
          hidden: { opacity: 0, y: 50 },
          visible: { opacity: 1, y: 0 },
          exit: { opacity: 0, y: -50 }
        }
      case 'slideRight':
        return {
          hidden: { opacity: 0, x: -100 },
          visible: { opacity: 1, x: 0 },
          exit: { opacity: 0, x: 100 }
        }
      case 'slideLeft':
        return {
          hidden: { opacity: 0, x: 100 },
          visible: { opacity: 1, x: 0 },
          exit: { opacity: 0, x: -100 }
        }
      case 'scaleUp':
        return {
          hidden: { opacity: 0, scale: 0.8 },
          visible: { opacity: 1, scale: 1 },
          exit: { opacity: 0, scale: 1.2 }
        }
      default:
        return {
          hidden: { opacity: 0 },
          visible: { opacity: 1 },
          exit: { opacity: 0 }
        }
    }
  }
  
  if (!isActive) return null
  
  return (
    <motion.div
      variants={getAnimationVariants()}
      initial="hidden"
      animate="visible"
      exit="exit"
      transition={{ duration: 0.6, ease: 'easeOut' }}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        padding: '2rem'
      }}
    >
      <Card
        sx={{
          maxWidth: 600,
          bgcolor: 'rgba(26, 26, 26, 0.9)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(76, 175, 80, 0.2)',
          borderRadius: 4,
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)'
        }}
      >
        <CardContent sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h4" color="#4CAF50" fontWeight="bold" mb={2}>
            {step.title}
          </Typography>
          
          <Typography variant="h6" color="white" mb={3} fontWeight="medium">
            {step.subtitle}
          </Typography>
          
          <Typography 
            variant="body1" 
            color="rgba(255,255,255,0.8)" 
            mb={4}
            lineHeight={1.6}
          >
            {step.description}
          </Typography>
          
          {step.id === 'developer' && (
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mb: 3 }}>
              <Chip 
                icon={<WorkIcon />}
                label="Software Engineer @ Louddoor" 
                sx={{ 
                  bgcolor: 'rgba(76, 175, 80, 0.2)', 
                  color: '#4CAF50',
                  border: '1px solid rgba(76, 175, 80, 0.3)'
                }} 
              />
              <Chip 
                icon={<SchoolIcon />}
                label="CS Student @ WGU" 
                sx={{ 
                  bgcolor: 'rgba(33, 150, 243, 0.2)', 
                  color: '#2196F3',
                  border: '1px solid rgba(33, 150, 243, 0.3)'
                }} 
              />
              <Chip 
                icon={<CodeIcon />}
                label="PHP • Laravel • Vue.js" 
                sx={{ 
                  bgcolor: 'rgba(255, 152, 0, 0.2)', 
                  color: '#FF9800',
                  border: '1px solid rgba(255, 152, 0, 0.3)'
                }} 
              />
            </Box>
          )}
          
          {step.actions && (
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 3 }}>
              {step.actions.map((action, index) => (
                <Button
                  key={index}
                  variant={action.primary ? 'contained' : 'outlined'}
                  size="large"
                  onClick={() => onAction(action.action)}
                  sx={{
                    ...(action.primary ? {
                      bgcolor: '#4CAF50',
                      '&:hover': { bgcolor: '#45a049' }
                    } : {
                      borderColor: '#4CAF50',
                      color: '#4CAF50',
                      '&:hover': { 
                        borderColor: '#45a049',
                        color: '#45a049',
                        bgcolor: 'rgba(76, 175, 80, 0.1)'
                      }
                    })
                  }}
                >
                  {action.label}
                </Button>
              ))}
            </Box>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

// Main Welcome Landing Experience Component
export const WelcomeLandingExperience: React.FC<WelcomeLandingExperienceProps> = ({
  onComplete,
  onSkip
}) => {
  const [loading, setLoading] = useState(true)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(true)
  const [isMuted, setIsMuted] = useState(false)
  const progressRef = useRef<NodeJS.Timeout | null>(null)
  
  // Auto-progress through steps
  useEffect(() => {
    if (!loading && isPlaying && currentStepIndex < welcomeSteps.length - 1) {
      const currentStep = welcomeSteps[currentStepIndex]
      
      progressRef.current = setTimeout(() => {
        setCurrentStepIndex(prev => prev + 1)
      }, currentStep.duration)
      
      return () => {
        if (progressRef.current) {
          clearTimeout(progressRef.current)
        }
      }
    }
  }, [currentStepIndex, loading, isPlaying])
  
  const handleLoadingComplete = () => {
    setLoading(false)
  }
  
  const handleStepAction = (action: () => void) => {
    if (currentStepIndex === welcomeSteps.length - 1) {
      // Last step - complete the welcome experience
      onComplete()
    } else {
      action()
    }
  }
  
  const handlePlayPause = () => {
    setIsPlaying(!isPlaying)
  }
  
  const handleNext = () => {
    if (currentStepIndex < welcomeSteps.length - 1) {
      setCurrentStepIndex(prev => prev + 1)
    } else {
      onComplete()
    }
  }
  
  const handlePrevious = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(prev => prev - 1)
    }
  }
  
  if (loading) {
    return <LoadingSequence onComplete={handleLoadingComplete} />
  }
  
  return (
    <Backdrop
      open={true}
      sx={{
        zIndex: 9998,
        bgcolor: 'rgba(10, 10, 10, 0.98)',
        backdropFilter: 'blur(10px)'
      }}
    >
      <Box
        sx={{
          position: 'relative',
          width: '100vw',
          height: '100vh',
          overflow: 'hidden'
        }}
      >
        {/* Background Pattern */}
        <Box
          sx={{
            position: 'absolute',
            inset: 0,
            backgroundImage: 'radial-gradient(circle at 25% 25%, rgba(76, 175, 80, 0.1) 0%, transparent 50%), radial-gradient(circle at 75% 75%, rgba(33, 150, 243, 0.1) 0%, transparent 50%)',
            animation: 'pulse 4s ease-in-out infinite alternate'
          }}
        />
        
        {/* Control Bar */}
        <Box
          sx={{
            position: 'absolute',
            top: 20,
            right: 20,
            display: 'flex',
            gap: 1,
            zIndex: 10
          }}
        >
          <IconButton
            onClick={handlePlayPause}
            sx={{ 
              color: 'white', 
              bgcolor: 'rgba(26, 26, 26, 0.8)',
              '&:hover': { bgcolor: 'rgba(76, 175, 80, 0.2)' }
            }}
          >
            {isPlaying ? <MuteIcon /> : <PlayIcon />}
          </IconButton>
          
          <IconButton
            onClick={onSkip}
            sx={{ 
              color: 'white', 
              bgcolor: 'rgba(26, 26, 26, 0.8)',
              '&:hover': { bgcolor: 'rgba(76, 175, 80, 0.2)' }
            }}
          >
            <SkipIcon />
          </IconButton>
          
          <IconButton
            onClick={onComplete}
            sx={{ 
              color: 'white', 
              bgcolor: 'rgba(26, 26, 26, 0.8)',
              '&:hover': { bgcolor: 'rgba(255, 82, 82, 0.2)' }
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
        
        {/* Progress Indicator */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 30,
            left: '50%',
            transform: 'translateX(-50%)',
            display: 'flex',
            gap: 1,
            zIndex: 10
          }}
        >
          {welcomeSteps.map((_, index) => (
            <Box
              key={index}
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                bgcolor: index === currentStepIndex ? '#4CAF50' : 'rgba(255,255,255,0.3)',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                '&:hover': {
                  bgcolor: index === currentStepIndex ? '#4CAF50' : 'rgba(255,255,255,0.5)'
                }
              }}
              onClick={() => setCurrentStepIndex(index)}
            />
          ))}
        </Box>
        
        {/* Navigation Arrows */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 100,
            left: '50%',
            transform: 'translateX(-50%)',
            display: 'flex',
            gap: 2,
            zIndex: 10
          }}
        >
          <Button
            onClick={handlePrevious}
            disabled={currentStepIndex === 0}
            variant="outlined"
            sx={{
              borderColor: 'rgba(255,255,255,0.3)',
              color: 'white',
              '&:hover': { borderColor: '#4CAF50', color: '#4CAF50' },
              '&:disabled': { 
                borderColor: 'rgba(255,255,255,0.1)',
                color: 'rgba(255,255,255,0.3)'
              }
            }}
          >
            Previous
          </Button>
          
          <Button
            onClick={handleNext}
            variant="contained"
            sx={{
              bgcolor: '#4CAF50',
              '&:hover': { bgcolor: '#45a049' }
            }}
          >
            {currentStepIndex === welcomeSteps.length - 1 ? 'Enter Garden' : 'Next'}
          </Button>
        </Box>
        
        {/* Welcome Steps */}
        <AnimatePresence mode="wait">
          <WelcomeStepCard
            key={currentStepIndex}
            step={welcomeSteps[currentStepIndex]}
            isActive={true}
            onAction={handleStepAction}
          />
        </AnimatePresence>
      </Box>
    </Backdrop>
  )
}