import React from 'react'
import { Box, IconButton, Tooltip, Fab } from '@mui/material'
import { 
  ExploreRounded,
  AutoAwesomeRounded,
  SettingsRounded,
  InfoRounded 
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'
import { useGardenStore } from '@/stores/gardenStore'

export const NavigationOverlay: React.FC = () => {
  const { navigationMode, setNavigationMode, ui, openModal } = useGardenStore()

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        pointerEvents: 'none',
        zIndex: 10
      }}
    >
      {/* Top Navigation Bar */}
      <Box
        sx={{
          position: 'absolute',
          top: 24,
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          gap: 2,
          pointerEvents: 'auto'
        }}
      >
        <motion.div
          className="glass-panel"
          style={{
            padding: '12px',
            borderRadius: '24px',
            display: 'flex',
            gap: '8px'
          }}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Tooltip title="Explore Mode">
            <IconButton
              onClick={() => setNavigationMode('explore')}
              sx={{
                color: navigationMode === 'explore' ? '#4CAF50' : 'rgba(255, 255, 255, 0.7)',
                '&:hover': { color: '#4CAF50' }
              }}
            >
              <ExploreRounded />
            </IconButton>
          </Tooltip>

          <Tooltip title="Focus Mode">
            <IconButton
              onClick={() => setNavigationMode('focus')}
              sx={{
                color: navigationMode === 'focus' ? '#2196F3' : 'rgba(255, 255, 255, 0.7)',
                '&:hover': { color: '#2196F3' }
              }}
            >
              <AutoAwesomeRounded />
            </IconButton>
          </Tooltip>

          <Tooltip title="Create Mode">
            <IconButton
              onClick={() => setNavigationMode('create')}
              sx={{
                color: navigationMode === 'create' ? '#FF9800' : 'rgba(255, 255, 255, 0.7)',
                '&:hover': { color: '#FF9800' }
              }}
            >
              <InfoRounded />
            </IconButton>
          </Tooltip>
        </motion.div>
      </Box>

      {/* Settings Button */}
      <motion.div
        style={{
          position: 'absolute',
          bottom: 24,
          right: 24,
          pointerEvents: 'auto'
        }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 1 }}
      >
        <Tooltip title="Settings">
          <Fab
            color="primary"
            onClick={() => openModal('settings')}
            sx={{
              background: 'linear-gradient(135deg, #4CAF50, #2E7D32)',
              '&:hover': {
                background: 'linear-gradient(135deg, #2E7D32, #1B5E20)'
              }
            }}
          >
            <SettingsRounded />
          </Fab>
        </Tooltip>
      </motion.div>
    </Box>
  )
}