import React from 'react'
import { Box, Alert, IconButton, Slide, Fade } from '@mui/material'
import { CloseRounded } from '@mui/icons-material'
import { AnimatePresence, motion } from 'framer-motion'
import { useGardenStore } from '@/stores/gardenStore'

export const NotificationSystem: React.FC = () => {
  const { ui, dismissNotification } = useGardenStore()

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 24,
        right: 24,
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
        pointerEvents: 'none'
      }}
    >
      <AnimatePresence>
        {ui.notifications.map((notification) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, x: 300, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 300, scale: 0.8 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            style={{ pointerEvents: 'auto' }}
          >
            <Alert
              severity={notification.type}
              sx={{
                maxWidth: 400,
                backdropFilter: 'blur(10px)',
                backgroundColor: 'rgba(26, 26, 26, 0.9)',
                border: '1px solid rgba(76, 175, 80, 0.2)',
                color: 'white',
                '& .MuiAlert-icon': {
                  color: notification.type === 'error' ? '#f44336' : 
                         notification.type === 'warning' ? '#ff9800' :
                         notification.type === 'success' ? '#4caf50' : '#2196f3'
                }
              }}
              action={
                <IconButton
                  size="small"
                  onClick={() => dismissNotification(notification.id)}
                  sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
                >
                  <CloseRounded fontSize="small" />
                </IconButton>
              }
            >
              {notification.message}
            </Alert>
          </motion.div>
        ))}
      </AnimatePresence>
    </Box>
  )
}