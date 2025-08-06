import React from 'react'
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  Typography, 
  Box, 
  Chip, 
  Button,
  IconButton
} from '@mui/material'
import { CloseRounded, LaunchRounded, CodeRounded } from '@mui/icons-material'
import { motion } from 'framer-motion'
import type { Project } from '@/types'

interface ProjectModalProps {
  project: Project
  open: boolean
  onClose: () => void
}

export const ProjectModal: React.FC<ProjectModalProps> = ({
  project,
  open,
  onClose
}) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
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
        <Typography variant="h4" sx={{ color: project.color.getHexString() }}>
          {project.name}
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
          <Typography variant="body1" paragraph>
            {project.description}
          </Typography>
          
          <Box sx={{ mb: 3, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {project.tags.map((tag) => (
              <Chip key={tag} label={tag} size="small" />
            ))}
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            {project.githubData && (
              <Button
                variant="outlined"
                startIcon={<CodeRounded />}
                onClick={() => window.open(project.githubData!.url, '_blank')}
              >
                View Code
              </Button>
            )}
            
            <Button
              variant="contained"
              startIcon={<LaunchRounded />}
              onClick={() => {
                // This would navigate to project demo
                console.log('Launch project:', project.name)
              }}
            >
              Launch Demo
            </Button>
          </Box>
        </motion.div>
      </DialogContent>
    </Dialog>
  )
}