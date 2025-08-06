import React from 'react'
import { createRoot } from 'react-dom/client'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import { CssBaseline } from '@mui/material'
import App from './App'
import './index.css'

// Create Material-UI theme with garden aesthetics
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#4CAF50', // Garden green
      light: '#8BC34A',
      dark: '#2E7D32',
    },
    secondary: {
      main: '#2196F3', // Sky blue
      light: '#64B5F6',
      dark: '#1976D2',
    },
    background: {
      default: '#0a0a0a', // Deep night
      paper: 'rgba(26, 26, 26, 0.9)', // Semi-transparent panels
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 300,
      fontSize: '3.5rem',
      letterSpacing: '-0.02em',
    },
    h2: {
      fontWeight: 300,
      fontSize: '2.5rem',
      letterSpacing: '-0.01em',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarColor: '#4CAF50 transparent',
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: '#4CAF50',
            borderRadius: '4px',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(145deg, rgba(26, 26, 26, 0.95), rgba(38, 38, 38, 0.9))',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(76, 175, 80, 0.1)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: '8px',
        },
      },
    },
  },
})

// Performance monitoring
const reportWebVitals = () => {
  if (import.meta.env.PROD) {
    import('./utils/webVitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(console.log)
      getFID(console.log)
      getFCP(console.log)
      getLCP(console.log)
      getTTFB(console.log)
    })
  }
}

const container = document.getElementById('root')
if (!container) throw new Error('Failed to find the root element')

const root = createRoot(container)

// React 18 Concurrent Features
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
)

// Register PWA service worker
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration)
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError)
      })
  })
}

reportWebVitals()