import React from 'react'
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  Typography, 
  Box,
  Slider,
  Switch,
  FormControlLabel,
  IconButton,
  Divider
} from '@mui/material'
import { CloseRounded } from '@mui/icons-material'
import { motion } from 'framer-motion'
import { useGardenStore, useSettingsSelector } from '@/stores/gardenStore'

interface SettingsPanelProps {
  open: boolean
  onClose: () => void
}

export const SettingsPanel: React.FC<SettingsPanelProps> = ({ open, onClose }) => {
  const settings = useSettingsSelector()
  const { updateSettings, setComplexityLevel } = useGardenStore()

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          background: 'linear-gradient(145deg, rgba(26, 26, 26, 0.95), rgba(38, 38, 38, 0.9))',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(76, 175, 80, 0.2)'
        }
      }}
    >
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">Garden Settings</Typography>
        <IconButton onClick={onClose}>
          <CloseRounded />
        </IconButton>
      </DialogTitle>
      
      <DialogContent>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Box sx={{ mb: 4 }}>
            <Typography gutterBottom>
              Visual Complexity: {settings.complexityLevel}
            </Typography>
            <Slider
              value={settings.complexityLevel}
              onChange={(_, value) => setComplexityLevel(value as any)}
              min={1}
              max={4}
              step={1}
              marks={[
                { value: 1, label: 'Low' },
                { value: 2, label: 'Medium' },
                { value: 3, label: 'High' },
                { value: 4, label: 'Ultra' }
              ]}
              sx={{ color: '#4CAF50' }}
            />
          </Box>

          <Divider sx={{ my: 2 }} />

          <FormControlLabel
            control={
              <Switch
                checked={settings.soundEnabled}
                onChange={(e) => updateSettings({ soundEnabled: e.target.checked })}
              />
            }
            label="Sound Effects"
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.particlesEnabled}
                onChange={(e) => updateSettings({ particlesEnabled: e.target.checked })}
              />
            }
            label="Particle Effects"
          />

          <FormControlLabel
            control={
              <Switch
                checked={settings.autoRotate}
                onChange={(e) => updateSettings({ autoRotate: e.target.checked })}
              />
            }
            label="Auto Rotate Camera"
          />
        </motion.div>
      </DialogContent>
    </Dialog>
  )
}