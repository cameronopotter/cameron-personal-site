import React, { useState, useEffect, useMemo } from 'react'
import { Box, Typography, LinearProgress, Fade, Chip } from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'
import { Eco, Visibility, Memory, Speed, TouchApp } from '@mui/icons-material'

interface EnhancedLoadingScreenProps {
  message?: string
  progress?: number
  deviceInfo?: {
    isMobile: boolean
    performanceLevel: 'low' | 'medium' | 'high'
    memoryLevel: 'low' | 'medium' | 'high'
    screenSize: 'small' | 'medium' | 'large' | 'xl'
  }
  optimizationSettings?: {
    complexityLevel: 1 | 2 | 3 | 4
    particlesEnabled: boolean
    weatherEnabled: boolean
  }
}

const loadingMessages = [
  "Growing your digital garden...",
  "Planting project seeds...",  
  "Nurturing code branches...",
  "Blooming with creativity...",
  "Cultivating innovation...",
  "Harvesting achievements...",
  "Tending to the ecosystem...",
  "Watering the roots of knowledge..."
]

const PlantIcon: React.FC<{ stage: number }> = ({ stage }) => {
  const icons = ['🌱', '🌿', '🌳', '🌸', '🌺']
  return (
    <motion.div
      key={stage}
      initial={{ scale: 0, rotate: -180 }}
      animate={{ scale: 1, rotate: 0 }}
      exit={{ scale: 0, rotate: 180 }}
      transition={{ duration: 0.8, ease: "easeInOut" }}
      style={{ fontSize: '3rem', display: 'inline-block' }}
    >
      {icons[stage % icons.length]}
    </motion.div>
  )
}

export const EnhancedLoadingScreen: React.FC<EnhancedLoadingScreenProps> = ({
  message = "Loading Digital Greenhouse...",
  progress = 0,
  deviceInfo,
  optimizationSettings
}) => {
  const [currentMessage, setCurrentMessage] = useState(0)
  const [animationStage, setAnimationStage] = useState(0)
  const [showOptimizations, setShowOptimizations] = useState(false)

  // Cycle through loading messages
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentMessage(prev => (prev + 1) % loadingMessages.length)
      setAnimationStage(prev => (prev + 1) % 5)
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  // Show optimization details after a moment
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowOptimizations(true)
    }, 1500)

    return () => clearTimeout(timer)
  }, [])

  const optimizationInfo = useMemo(() => {
    if (!deviceInfo || !optimizationSettings) return []

    const info = []

    // Device type
    info.push({
      icon: deviceInfo.isMobile ? <TouchApp /> : <Visibility />,
      label: deviceInfo.isMobile ? 'Mobile Optimized' : 'Desktop Experience',
      color: deviceInfo.isMobile ? '#4CAF50' : '#2196F3'
    })

    // Performance level
    const performanceColors = { low: '#FF9800', medium: '#4CAF50', high: '#2196F3' }
    info.push({
      icon: <Speed />,
      label: `${deviceInfo.performanceLevel.toUpperCase()} Performance`,
      color: performanceColors[deviceInfo.performanceLevel]
    })

    // Memory optimization
    const memoryColors = { low: '#F44336', medium: '#FF9800', high: '#4CAF50' }
    info.push({
      icon: <Memory />,
      label: `Memory: ${deviceInfo.memoryLevel.toUpperCase()}`,
      color: memoryColors[deviceInfo.memoryLevel]
    })

    // Quality level
    info.push({
      icon: <Eco />,
      label: `Quality Level ${optimizationSettings.complexityLevel}`,
      color: '#4CAF50'
    })

    return info
  }, [deviceInfo, optimizationSettings])

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%)',
        zIndex: 9999,
        overflow: 'hidden'
      }}
    >
      {/* Animated background particles */}
      <Box
        sx={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          background: `
            radial-gradient(circle at 20% 50%, rgba(76, 175, 80, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(33, 150, 243, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 80%, rgba(156, 39, 176, 0.1) 0%, transparent 50%)
          `,
          animation: 'float 6s ease-in-out infinite'
        }}
      />

      <style>
        {`
          @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-10px) rotate(180deg); }
          }
        `}
      </style>

      {/* Main loading content */}
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          {/* Animated plant icon */}
          <Box sx={{ mb: 3, height: 80, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <AnimatePresence mode="wait">
              <PlantIcon stage={animationStage} />
            </AnimatePresence>
          </Box>

          {/* Main title */}
          <Typography 
            variant="h3" 
            sx={{ 
              color: 'white', 
              fontWeight: 'bold', 
              mb: 2,
              background: 'linear-gradient(45deg, #4CAF50 30%, #2196F3 90%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            Digital Greenhouse
          </Typography>

          {/* Animated loading message */}
          <Box sx={{ height: 60, display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 3 }}>
            <AnimatePresence mode="wait">
              <motion.div
                key={currentMessage}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <Typography variant="h6" color="rgba(255,255,255,0.8)" textAlign="center">
                  {loadingMessages[currentMessage]}
                </Typography>
              </motion.div>
            </AnimatePresence>
          </Box>

          {/* Progress bar */}
          {progress > 0 && (
            <Box sx={{ width: 300, mb: 3 }}>
              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  bgcolor: 'rgba(255,255,255,0.1)',
                  '& .MuiLinearProgress-bar': {
                    background: 'linear-gradient(45deg, #4CAF50 30%, #2196F3 90%)',
                    borderRadius: 3
                  }
                }}
              />
              <Typography variant="body2" color="rgba(255,255,255,0.6)" textAlign="center" sx={{ mt: 1 }}>
                {Math.round(progress)}% Complete
              </Typography>
            </Box>
          )}
        </Box>

        {/* Optimization info */}
        <Fade in={showOptimizations} timeout={1000}>
          <Box sx={{ mt: 4 }}>
            <Typography variant="body2" color="rgba(255,255,255,0.5)" textAlign="center" sx={{ mb: 2 }}>
              Optimizing for your device
            </Typography>
            <Box sx={{ 
              display: 'flex', 
              flexWrap: 'wrap', 
              gap: 1, 
              justifyContent: 'center',
              maxWidth: 400,
              mx: 'auto'
            }}>
              {optimizationInfo.map((info, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.2, duration: 0.4 }}
                >
                  <Chip
                    icon={React.cloneElement(info.icon, { sx: { color: info.color } })}
                    label={info.label}
                    variant="outlined"
                    size="small"
                    sx={{
                      color: 'white',
                      borderColor: `${info.color}50`,
                      bgcolor: `${info.color}15`,
                      '& .MuiChip-icon': {
                        color: info.color
                      }
                    }}
                  />
                </motion.div>
              ))}
            </Box>
          </Box>
        </Fade>

        {/* Subtle hint text */}
        <Fade in timeout={3000}>
          <Typography 
            variant="caption" 
            color="rgba(255,255,255,0.4)" 
            textAlign="center"
            sx={{ mt: 4, display: 'block' }}
          >
            Cameron Potter's Interactive Portfolio
          </Typography>
        </Fade>
      </motion.div>
    </Box>
  )
}