import React from 'react'
import { Box, Typography, Paper, Grid, Chip } from '@mui/material'
import { usePerformanceSelector } from '@/stores/gardenStore'

export const PerformanceMonitor: React.FC = () => {
  const performance = usePerformanceSelector()

  // Only show in development
  if (import.meta.env.PROD) return null

  const getPerformanceColor = (fps: number) => {
    if (fps >= 60) return '#4CAF50'
    if (fps >= 30) return '#FF9800'
    return '#f44336'
  }

  const getMemoryColor = (memory: number) => {
    if (memory < 50) return '#4CAF50'
    if (memory < 100) return '#FF9800'
    return '#f44336'
  }

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 16,
        right: 16,
        zIndex: 9999,
        pointerEvents: 'none'
      }}
    >
      <Paper
        sx={{
          p: 2,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          color: 'white',
          minWidth: 200,
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(76, 175, 80, 0.2)'
        }}
      >
        <Typography variant="h6" gutterBottom>
          Performance Monitor
        </Typography>
        
        <Grid container spacing={1}>
          <Grid item xs={6}>
            <Typography variant="body2">FPS:</Typography>
          </Grid>
          <Grid item xs={6}>
            <Chip
              label={performance.fps}
              size="small"
              sx={{
                backgroundColor: getPerformanceColor(performance.fps),
                color: 'white',
                fontSize: '0.75rem'
              }}
            />
          </Grid>
          
          <Grid item xs={6}>
            <Typography variant="body2">Render:</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" sx={{ color: getPerformanceColor(60000 / performance.renderTime) }}>
              {performance.renderTime.toFixed(2)}ms
            </Typography>
          </Grid>
          
          <Grid item xs={6}>
            <Typography variant="body2">Memory:</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" sx={{ color: getMemoryColor(performance.memoryUsage) }}>
              {performance.memoryUsage}MB
            </Typography>
          </Grid>
          
          {performance.isOptimizedMode && (
            <Grid item xs={12}>
              <Chip
                label="Optimized Mode"
                size="small"
                sx={{
                  backgroundColor: '#FF9800',
                  color: 'white',
                  fontSize: '0.7rem'
                }}
              />
            </Grid>
          )}
        </Grid>
      </Paper>
    </Box>
  )
}