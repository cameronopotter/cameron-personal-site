import React from 'react'
import { Box, CircularProgress, Typography, LinearProgress } from '@mui/material'
import { motion } from 'framer-motion'

interface LoadingScreenProps {
  message?: string
  progress?: number
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  message = "Preparing your digital garden...",
  progress
}) => {
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
        background: 'linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%)',
        zIndex: 9999
      }}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        style={{ textAlign: 'center' }}
      >
        <Typography 
          variant="h4" 
          gutterBottom 
          sx={{ 
            mb: 4,
            background: 'linear-gradient(135deg, #4CAF50, #2196F3)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: 300
          }}
        >
          Digital Greenhouse
        </Typography>
        
        {progress !== undefined ? (
          <Box sx={{ width: '300px', mb: 2 }}>
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: '#4CAF50'
                }
              }}
            />
            <Typography variant="body2" sx={{ mt: 1, color: 'rgba(255, 255, 255, 0.7)' }}>
              {Math.round(progress)}%
            </Typography>
          </Box>
        ) : (
          <CircularProgress 
            size={60} 
            sx={{ 
              color: '#4CAF50',
              mb: 3
            }} 
          />
        )}
        
        <Typography 
          variant="body1" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.8)',
            maxWidth: '400px'
          }}
        >
          {message}
        </Typography>
      </motion.div>
    </Box>
  )
}