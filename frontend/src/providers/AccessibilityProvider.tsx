import React, { createContext, useContext, useEffect, useState } from 'react'
import { useGardenStore } from '@/stores/gardenStore'

interface AccessibilityContextType {
  reducedMotion: boolean
  highContrast: boolean
  screenReaderMode: boolean
  keyboardNavigation: boolean
  announceChanges: (message: string) => void
}

const AccessibilityContext = createContext<AccessibilityContextType | null>(null)

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext)
  if (!context) {
    throw new Error('useAccessibility must be used within AccessibilityProvider')
  }
  return context
}

interface AccessibilityProviderProps {
  children: React.ReactNode
}

export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({ children }) => {
  const [reducedMotion, setReducedMotion] = useState(false)
  const [highContrast, setHighContrast] = useState(false)
  const [screenReaderMode, setScreenReaderMode] = useState(false)
  const [keyboardNavigation, setKeyboardNavigation] = useState(false)
  
  const { showNotification, updateSettings } = useGardenStore()
  
  // Check for media queries and preferences
  useEffect(() => {
    // Reduced motion preference
    const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReducedMotion(reducedMotionQuery.matches)
    
    const handleReducedMotionChange = (e: MediaQueryListEvent) => {
      setReducedMotion(e.matches)
      if (e.matches) {
        updateSettings({
          complexityLevel: 1,
          particlesEnabled: false,
          autoRotate: false
        })
      }
    }
    
    reducedMotionQuery.addEventListener('change', handleReducedMotionChange)
    
    // High contrast preference
    const highContrastQuery = window.matchMedia('(prefers-contrast: high)')
    setHighContrast(highContrastQuery.matches)
    
    const handleHighContrastChange = (e: MediaQueryListEvent) => {
      setHighContrast(e.matches)
    }
    
    highContrastQuery.addEventListener('change', handleHighContrastChange)
    
    // Screen reader detection (basic)
    const checkScreenReader = () => {
      return navigator.userAgent.includes('NVDA') || 
             navigator.userAgent.includes('JAWS') ||
             window.speechSynthesis.speaking
    }
    
    setScreenReaderMode(checkScreenReader())
    
    return () => {
      reducedMotionQuery.removeEventListener('change', handleReducedMotionChange)
      highContrastQuery.removeEventListener('change', handleHighContrastChange)
    }
  }, [updateSettings])
  
  // Keyboard navigation detection
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        setKeyboardNavigation(true)
      }
    }
    
    const handleMouseDown = () => {
      setKeyboardNavigation(false)
    }
    
    document.addEventListener('keydown', handleKeyDown)
    document.addEventListener('mousedown', handleMouseDown)
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.removeEventListener('mousedown', handleMouseDown)
    }
  }, [])
  
  const announceChanges = (message: string) => {
    // Update the aria-live region
    const announcer = document.getElementById('garden-announcements')
    if (announcer) {
      announcer.textContent = message
      
      // Clear after a delay to allow for repeated announcements
      setTimeout(() => {
        announcer.textContent = ''
      }, 1000)
    }
    
    // Also show as notification for visual users
    if (!screenReaderMode) {
      showNotification({
        type: 'info',
        message,
        duration: 2000,
        persistent: false
      })
    }
  }
  
  return (
    <AccessibilityContext.Provider
      value={{
        reducedMotion,
        highContrast,
        screenReaderMode,
        keyboardNavigation,
        announceChanges
      }}
    >
      {children}
    </AccessibilityContext.Provider>
  )
}