import React from 'react'
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  Typography, 
  Box, 
  LinearProgress,
  IconButton 
} from '@mui/material'
import { CloseRounded } from '@mui/icons-material'
import { motion } from 'framer-motion'
import type { Skill } from '@/types'

interface SkillConstellationModalProps {
  skill: Skill
  open: boolean
  onClose: () => void
}

export const SkillConstellationModal: React.FC<SkillConstellationModalProps> = ({
  skill,
  open,
  onClose
}) => {
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
        <Typography variant="h5">
          {skill.name}
        </Typography>
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
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" gutterBottom>
              Proficiency: {Math.round(skill.proficiency * 100)}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={skill.proficiency * 100}
              sx={{ 
                height: 8, 
                borderRadius: 4,
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: '#4CAF50'
                }
              }}
            />
          </Box>
          
          <Typography variant="body2" gutterBottom>
            Experience: {skill.experience} years
          </Typography>
          
          <Typography variant="body2" gutterBottom>
            Projects: {skill.projects.length}
          </Typography>
          
          <Typography variant="body2" gutterBottom>
            Category: {skill.category}
          </Typography>
        </motion.div>
      </DialogContent>
    </Dialog>
  )
}