import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Box, Typography, Button, Alert } from '@mui/material'
import { RefreshRounded, BugReportRounded } from '@mui/icons-material'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null
  }

  public static getDerivedStateFromError(error: Error): State {
    return { 
      hasError: true, 
      error,
      errorInfo: null 
    }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Garden Error Boundary caught an error:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo
    })
    
    // Report to error tracking service in production
    if (import.meta.env.PROD) {
      // This would integrate with Sentry or similar
      console.error('Production error:', error, errorInfo)
    }
  }

  private handleReload = () => {
    window.location.reload()
  }

  private handleReport = () => {
    const { error, errorInfo } = this.state
    const errorData = {
      error: error?.toString(),
      stack: error?.stack,
      componentStack: errorInfo?.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    }
    
    console.log('Error report data:', errorData)
    // This would send to error reporting service
  }

  public render() {
    if (this.state.hasError) {
      return (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100vh',
            p: 4,
            textAlign: 'center',
            background: 'linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%)'
          }}
        >
          <Alert 
            severity="error" 
            sx={{ 
              mb: 4,
              maxWidth: 600,
              '& .MuiAlert-icon': {
                fontSize: '2rem'
              }
            }}
          >
            <Typography variant="h5" gutterBottom>
              Oops! The garden encountered an error
            </Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>
              Something went wrong while growing your digital garden. Don't worry, 
              your data is safe and we can get you back up and running.
            </Typography>
          </Alert>

          <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<RefreshRounded />}
              onClick={this.handleReload}
              sx={{
                background: 'linear-gradient(135deg, #4CAF50, #2E7D32)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #2E7D32, #1B5E20)'
                }
              }}
            >
              Restart Garden
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<BugReportRounded />}
              onClick={this.handleReport}
              sx={{
                borderColor: '#4CAF50',
                color: '#4CAF50',
                '&:hover': {
                  borderColor: '#2E7D32',
                  backgroundColor: 'rgba(76, 175, 80, 0.1)'
                }
              }}
            >
              Report Issue
            </Button>
          </Box>

          {/* Development error details */}
          {import.meta.env.DEV && this.state.error && (
            <Box
              sx={{
                maxWidth: 800,
                p: 3,
                bgcolor: 'rgba(255, 0, 0, 0.1)',
                borderRadius: 2,
                border: '1px solid rgba(255, 0, 0, 0.3)',
                textAlign: 'left'
              }}
            >
              <Typography variant="h6" gutterBottom color="error">
                Development Error Details:
              </Typography>
              <Typography 
                variant="body2" 
                component="pre" 
                sx={{ 
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  fontSize: '0.75rem',
                  color: '#ff6b6b',
                  maxHeight: '300px',
                  overflow: 'auto'
                }}
              >
                {this.state.error.toString()}
                {this.state.error.stack && `\n\nStack:\n${this.state.error.stack}`}
                {this.state.errorInfo?.componentStack && 
                  `\n\nComponent Stack:${this.state.errorInfo.componentStack}`
                }
              </Typography>
            </Box>
          )}
        </Box>
      )
    }

    return this.props.children
  }
}