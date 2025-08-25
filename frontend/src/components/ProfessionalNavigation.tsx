import React, { useState, useEffect } from 'react'
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Chip,
  Backdrop,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Fade
} from '@mui/material'
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  Person as PersonIcon,
  Work as WorkIcon,
  Code as CodeIcon,
  GitHub as GitHubIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  School as SchoolIcon,
  Nature as NatureIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  Brightness4 as ThemeIcon,
  Info as InfoIcon,
  Home as HomeIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'
import { useGardenStore } from '@/stores/gardenStore'

interface ProfessionalNavigationProps {
  onNavigate: (section: string) => void
  currentSection: string
}

interface NavigationSection {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  color: string
  action?: () => void
}

const navigationSections: NavigationSection[] = [
  {
    id: 'garden',
    title: 'Digital Garden',
    description: 'Explore my projects as living plants',
    icon: <NatureIcon />,
    color: '#4CAF50'
  },
  {
    id: 'about',
    title: 'About Cameron',
    description: 'Professional background and experience',
    icon: <PersonIcon />,
    color: '#2196F3'
  },
  {
    id: 'projects',
    title: 'Project Portfolio',
    description: 'Detailed view of my work and contributions',
    icon: <WorkIcon />,
    color: '#FF9800'
  },
  {
    id: 'skills',
    title: 'Technical Skills',
    description: 'Programming languages, frameworks, and tools',
    icon: <CodeIcon />,
    color: '#9C27B0'
  },
  {
    id: 'github',
    title: 'GitHub Activity',
    description: 'Contribution history and code statistics',
    icon: <GitHubIcon />,
    color: '#333333'
  },
  {
    id: 'contact',
    title: 'Get In Touch',
    description: 'Connect with me for opportunities',
    icon: <EmailIcon />,
    color: '#F44336'
  }
]

// Professional Header Component
const ProfessionalHeader: React.FC<{
  onMenuClick: () => void
  onProfileClick: () => void
  currentSection: string
}> = ({ onMenuClick, onProfileClick, currentSection }) => {
  const [scrolled, setScrolled] = useState(false)
  
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }
    
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])
  
  const getCurrentSectionTitle = () => {
    const section = navigationSections.find(s => s.id === currentSection)
    return section?.title || 'Digital Greenhouse'
  }
  
  return (
    <AppBar 
      position="fixed" 
      sx={{
        bgcolor: scrolled ? 'rgba(26, 26, 26, 0.95)' : 'transparent',
        backdropFilter: scrolled ? 'blur(20px)' : 'none',
        transition: 'all 0.3s ease',
        borderBottom: scrolled ? '1px solid rgba(76, 175, 80, 0.2)' : 'none',
        boxShadow: scrolled ? '0 4px 20px rgba(0,0,0,0.3)' : 'none'
      }}
      elevation={0}
    >
      <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 2, md: 4 } }}>
        {/* Left: Menu and Title */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton
            onClick={onMenuClick}
            sx={{ 
              color: '#4CAF50',
              '&:hover': { bgcolor: 'rgba(76, 175, 80, 0.1)' }
            }}
          >
            <MenuIcon />
          </IconButton>
          
          <Box>
            <Typography 
              variant="h6" 
              sx={{ 
                color: 'white', 
                fontWeight: 'bold',
                display: { xs: 'none', sm: 'block' }
              }}
            >
              {getCurrentSectionTitle()}
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                color: 'rgba(255,255,255,0.7)',
                display: { xs: 'none', md: 'block' }
              }}
            >
              Cameron Potter • Full-Stack Developer
            </Typography>
          </Box>
        </Box>
        
        {/* Right: Profile and Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Button
            startIcon={<GitHubIcon />}
            onClick={() => window.open('https://github.com/cameronopotter', '_blank')}
            sx={{
              color: 'white',
              borderColor: 'rgba(255,255,255,0.3)',
              '&:hover': { borderColor: '#4CAF50', color: '#4CAF50' },
              display: { xs: 'none', md: 'flex' }
            }}
            variant="outlined"
            size="small"
          >
            GitHub
          </Button>
          
          <Avatar
            onClick={onProfileClick}
            sx={{
              width: 40,
              height: 40,
              bgcolor: '#4CAF50',
              cursor: 'pointer',
              '&:hover': { bgcolor: '#45a049' },
              fontWeight: 'bold'
            }}
          >
            CP
          </Avatar>
        </Box>
      </Toolbar>
    </AppBar>
  )
}

// Navigation Drawer Component
const NavigationDrawer: React.FC<{
  open: boolean
  onClose: () => void
  onNavigate: (section: string) => void
  currentSection: string
}> = ({ open, onClose, onNavigate, currentSection }) => {
  
  const handleNavigate = (sectionId: string) => {
    onNavigate(sectionId)
    onClose()
  }
  
  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: { xs: '100vw', sm: 400 },
          bgcolor: 'rgba(26, 26, 26, 0.98)',
          backdropFilter: 'blur(20px)',
          border: 'none',
          borderRight: '1px solid rgba(76, 175, 80, 0.2)'
        }
      }}
      ModalProps={{
        BackdropComponent: Backdrop,
        BackdropProps: {
          sx: { bgcolor: 'rgba(0,0,0,0.8)' }
        }
      }}
    >
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box sx={{ p: 3, borderBottom: '1px solid rgba(76, 175, 80, 0.2)' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5" color="white" fontWeight="bold">
              Portfolio Navigation
            </Typography>
            <IconButton onClick={onClose} sx={{ color: 'white' }}>
              <CloseIcon />
            </IconButton>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ width: 60, height: 60, bgcolor: '#4CAF50', fontSize: '1.5rem' }}>
              CP
            </Avatar>
            <Box>
              <Typography variant="h6" color="white" fontWeight="bold">
                Cameron Potter
              </Typography>
              <Typography variant="body2" color="rgba(255,255,255,0.7)">
                Full-Stack Software Engineer
              </Typography>
              <Typography variant="body2" color="#4CAF50">
                Columbia, SC
              </Typography>
            </Box>
          </Box>
        </Box>
        
        {/* Navigation Sections */}
        <Box sx={{ flex: 1, overflowY: 'auto' }}>
          <List sx={{ px: 2, py: 2 }}>
            {navigationSections.map((section, index) => (
              <motion.div
                key={section.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <ListItem
                  button
                  onClick={() => handleNavigate(section.id)}
                  sx={{
                    borderRadius: 2,
                    mb: 1,
                    bgcolor: currentSection === section.id ? 
                      'rgba(76, 175, 80, 0.1)' : 'transparent',
                    border: currentSection === section.id ? 
                      '1px solid rgba(76, 175, 80, 0.3)' : '1px solid transparent',
                    '&:hover': {
                      bgcolor: 'rgba(76, 175, 80, 0.05)',
                      border: '1px solid rgba(76, 175, 80, 0.2)'
                    },
                    transition: 'all 0.2s ease'
                  }}
                >
                  <ListItemIcon
                    sx={{
                      color: currentSection === section.id ? '#4CAF50' : section.color,
                      minWidth: 40
                    }}
                  >
                    {section.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography 
                        variant="subtitle1" 
                        color={currentSection === section.id ? '#4CAF50' : 'white'}
                        fontWeight={currentSection === section.id ? 'bold' : 'normal'}
                      >
                        {section.title}
                      </Typography>
                    }
                    secondary={
                      <Typography 
                        variant="body2" 
                        color="rgba(255,255,255,0.6)"
                        sx={{ mt: 0.5 }}
                      >
                        {section.description}
                      </Typography>
                    }
                  />
                </ListItem>
              </motion.div>
            ))}
          </List>
        </Box>
        
        {/* Footer with Contact Info */}
        <Box sx={{ p: 3, borderTop: '1px solid rgba(76, 175, 80, 0.2)' }}>
          <Typography variant="subtitle2" color="#4CAF50" mb={2} fontWeight="bold">
            Quick Contact
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Button
              startIcon={<EmailIcon />}
              href="mailto:cameronopotter@gmail.com"
              sx={{ 
                justifyContent: 'flex-start', 
                color: 'white',
                '&:hover': { color: '#4CAF50' }
              }}
              size="small"
            >
              cameronopotter@gmail.com
            </Button>
            <Button
              startIcon={<PhoneIcon />}
              href="tel:8036036393"
              sx={{ 
                justifyContent: 'flex-start', 
                color: 'white',
                '&:hover': { color: '#4CAF50' }
              }}
              size="small"
            >
              (803) 603-6393
            </Button>
          </Box>
          
          <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip 
              label="Available for Hire" 
              size="small" 
              sx={{ 
                bgcolor: 'rgba(76, 175, 80, 0.2)', 
                color: '#4CAF50',
                border: '1px solid rgba(76, 175, 80, 0.3)'
              }} 
            />
            <Chip 
              label="Remote Ready" 
              size="small" 
              sx={{ 
                bgcolor: 'rgba(33, 150, 243, 0.2)', 
                color: '#2196F3',
                border: '1px solid rgba(33, 150, 243, 0.3)'
              }} 
            />
          </Box>
        </Box>
      </Box>
    </Drawer>
  )
}

// Main Professional Navigation Component
export const ProfessionalNavigation: React.FC<ProfessionalNavigationProps> = ({
  onNavigate,
  currentSection
}) => {
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [profileMenuAnchor, setProfileMenuAnchor] = useState<null | HTMLElement>(null)
  
  const handleMenuClick = () => {
    setDrawerOpen(true)
  }
  
  const handleProfileClick = (event: React.MouseEvent<HTMLElement>) => {
    setProfileMenuAnchor(event.currentTarget)
  }
  
  const handleProfileMenuClose = () => {
    setProfileMenuAnchor(null)
  }
  
  const handleDrawerClose = () => {
    setDrawerOpen(false)
  }
  
  return (
    <>
      {/* Professional Header */}
      <ProfessionalHeader
        onMenuClick={handleMenuClick}
        onProfileClick={handleProfileClick}
        currentSection={currentSection}
      />
      
      {/* Navigation Drawer */}
      <NavigationDrawer
        open={drawerOpen}
        onClose={handleDrawerClose}
        onNavigate={onNavigate}
        currentSection={currentSection}
      />
      
      {/* Profile Menu */}
      <Menu
        anchorEl={profileMenuAnchor}
        open={Boolean(profileMenuAnchor)}
        onClose={handleProfileMenuClose}
        PaperProps={{
          sx: {
            bgcolor: 'rgba(26, 26, 26, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(76, 175, 80, 0.2)',
            mt: 1
          }
        }}
      >
        <MenuItem onClick={() => { onNavigate('about'); handleProfileMenuClose() }}>
          <PersonIcon sx={{ mr: 2, color: '#4CAF50' }} />
          <Typography color="white">View Profile</Typography>
        </MenuItem>
        <MenuItem onClick={() => { onNavigate('github'); handleProfileMenuClose() }}>
          <GitHubIcon sx={{ mr: 2, color: '#4CAF50' }} />
          <Typography color="white">GitHub Activity</Typography>
        </MenuItem>
        <Divider sx={{ borderColor: 'rgba(76, 175, 80, 0.2)' }} />
        <MenuItem onClick={() => window.open('mailto:cameronopotter@gmail.com')}>
          <EmailIcon sx={{ mr: 2, color: '#4CAF50' }} />
          <Typography color="white">Email Me</Typography>
        </MenuItem>
      </Menu>
    </>
  )
}