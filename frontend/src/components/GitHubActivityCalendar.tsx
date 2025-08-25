import React, { useState, useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Text, Html, RoundedBox } from '@react-three/drei'
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Tooltip,
  CircularProgress
} from '@mui/material'
import { motion } from 'framer-motion'
import { useSpring, animated } from '@react-spring/three'
import { Group, Vector3, Color } from 'three'
import { GitHub, TrendingUp, CalendarToday } from '@mui/icons-material'

interface GitHubActivityCalendarProps {
  position: [number, number, number]
  visible: boolean
  onClose: () => void
  githubUsername: string
}

interface CommitData {
  date: string
  count: number
  level: number // 0-4 intensity level
}

interface GitHubStats {
  totalCommits: number
  currentStreak: number
  longestStreak: number
  averagePerDay: number
  mostActiveDay: string
  commits: CommitData[]
}

// Mock GitHub data (in real implementation, this would come from GitHub API)
const generateMockGitHubData = (): GitHubStats => {
  const commits: CommitData[] = []
  const today = new Date()
  const oneYear = 365
  
  let totalCommits = 0
  let currentStreak = 0
  let longestStreak = 0
  let tempStreak = 0
  
  // Generate data for the past year
  for (let i = oneYear; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    
    // Simulate realistic commit patterns (more commits on weekdays)
    const isWeekday = date.getDay() >= 1 && date.getDay() <= 5
    const baseChance = isWeekday ? 0.7 : 0.3
    
    // Add some project bursts and vacation periods
    const dayOfYear = Math.floor((date.getTime() - new Date(date.getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24))
    const isProjectBurst = Math.sin(dayOfYear / 30) > 0.5
    const isVacation = dayOfYear >= 100 && dayOfYear <= 107 // Mock vacation week
    
    let count = 0
    if (!isVacation) {
      const chance = baseChance * (isProjectBurst ? 1.5 : 1)
      if (Math.random() < chance) {
        count = Math.floor(Math.random() * (isProjectBurst ? 8 : 4)) + 1
      }
    }
    
    totalCommits += count
    
    // Calculate streaks
    if (count > 0) {
      tempStreak++
      if (i === 0) currentStreak = tempStreak // Current streak if today has commits
    } else {
      longestStreak = Math.max(longestStreak, tempStreak)
      tempStreak = 0
      if (i === 0) currentStreak = 0
    }
    
    // Determine intensity level (0-4)
    const level = count === 0 ? 0 : 
                 count <= 1 ? 1 :
                 count <= 3 ? 2 :
                 count <= 6 ? 3 : 4
    
    commits.push({
      date: date.toISOString().split('T')[0],
      count,
      level
    })
  }
  
  longestStreak = Math.max(longestStreak, tempStreak)
  const averagePerDay = Math.round((totalCommits / oneYear) * 10) / 10
  
  // Find most active day
  const dayStats = commits.reduce((acc, commit) => {
    const day = new Date(commit.date).toLocaleDateString('en-US', { weekday: 'long' })
    acc[day] = (acc[day] || 0) + commit.count
    return acc
  }, {} as Record<string, number>)
  
  const mostActiveDay = Object.entries(dayStats).reduce((max, [day, count]) => 
    count > max.count ? { day, count } : max, 
    { day: '', count: 0 }
  ).day
  
  return {
    totalCommits,
    currentStreak,
    longestStreak,
    averagePerDay,
    mostActiveDay,
    commits: commits.reverse() // Most recent first
  }
}

// 3D Calendar Grid Component
const Calendar3D: React.FC<{
  commits: CommitData[]
  position: [number, number, number]
  onDayHover: (commit: CommitData | null) => void
}> = ({ commits, position, onDayHover }) => {
  const groupRef = useRef<Group>(null!)
  const weeksInYear = 53
  const daysInWeek = 7
  
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.x = Math.sin(state.clock.getElapsedTime() * 0.2) * 0.05
      groupRef.current.rotation.y = Math.sin(state.clock.getElapsedTime() * 0.3) * 0.1
    }
  })
  
  // Color mapping for different activity levels
  const getLevelColor = (level: number): string => {
    const colors = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']
    return colors[level] || colors[0]
  }
  
  return (
    <group ref={groupRef} position={position}>
      {commits.map((commit, index) => {
        const week = Math.floor(index / daysInWeek)
        const day = index % daysInWeek
        
        const x = (week - weeksInYear / 2) * 0.15
        const y = (3.5 - day) * 0.15
        const z = commit.level * 0.02 // Slight depth based on activity
        
        return (
          <RoundedBox
            key={commit.date}
            args={[0.12, 0.12, 0.02 + commit.level * 0.01]}
            position={[x, y, z]}
            radius={0.01}
            smoothness={4}
            onPointerOver={() => onDayHover(commit)}
            onPointerOut={() => onDayHover(null)}
          >
            <meshStandardMaterial
              color={getLevelColor(commit.level)}
              emissive={getLevelColor(commit.level)}
              emissiveIntensity={commit.level > 0 ? 0.1 : 0}
            />
          </RoundedBox>
        )
      })}
      
      {/* Month labels */}
      {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].map((month, index) => (
        <Text
          key={month}
          position={[(index * 4.4 - 22) * 0.15, -0.8, 0]}
          fontSize={0.1}
          color="rgba(255,255,255,0.6)"
          anchorX="center"
          font="/fonts/Inter-Medium.woff"
        >
          {month}
        </Text>
      ))}
      
      {/* Day labels */}
      {['Mon', 'Wed', 'Fri'].map((day, index) => (
        <Text
          key={day}
          position={[-4.2, 2 - index * 2 * 0.15, 0]}
          fontSize={0.08}
          color="rgba(255,255,255,0.6)"
          anchorX="right"
          font="/fonts/Inter-Medium.woff"
        >
          {day}
        </Text>
      ))}
      
      {/* Title */}
      <Text
        position={[0, 1.2, 0]}
        fontSize={0.15}
        color="#4CAF50"
        anchorX="center"
        font="/fonts/Inter-Bold.woff"
      >
        GitHub Contributions
      </Text>
    </group>
  )
}

// Stats Display Component
const StatsDisplay: React.FC<{ stats: GitHubStats }> = ({ stats }) => (
  <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2, mb: 3 }}>
    <Card sx={{ bgcolor: 'rgba(255,255,255,0.05)', p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <TrendingUp sx={{ color: '#4CAF50', mr: 1 }} />
        <Typography variant="h6" color="white">Total Commits</Typography>
      </Box>
      <Typography variant="h4" color="#4CAF50" fontWeight="bold">
        {stats.totalCommits.toLocaleString()}
      </Typography>
    </Card>
    
    <Card sx={{ bgcolor: 'rgba(255,255,255,0.05)', p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <CalendarToday sx={{ color: '#2196F3', mr: 1 }} />
        <Typography variant="h6" color="white">Current Streak</Typography>
      </Box>
      <Typography variant="h4" color="#2196F3" fontWeight="bold">
        {stats.currentStreak} days
      </Typography>
    </Card>
    
    <Card sx={{ bgcolor: 'rgba(255,255,255,0.05)', p: 2 }}>
      <Typography variant="body2" color="rgba(255,255,255,0.7)" mb={0.5}>
        Longest Streak
      </Typography>
      <Typography variant="h5" color="white" fontWeight="bold">
        {stats.longestStreak} days
      </Typography>
    </Card>
    
    <Card sx={{ bgcolor: 'rgba(255,255,255,0.05)', p: 2 }}>
      <Typography variant="body2" color="rgba(255,255,255,0.7)" mb={0.5}>
        Average per Day
      </Typography>
      <Typography variant="h5" color="white" fontWeight="bold">
        {stats.averagePerDay}
      </Typography>
    </Card>
  </Box>
)

// Main GitHub Activity Calendar Component
export const GitHubActivityCalendar: React.FC<GitHubActivityCalendarProps> = ({
  position,
  visible,
  onClose,
  githubUsername
}) => {
  const [stats, setStats] = useState<GitHubStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [hoveredDay, setHoveredDay] = useState<CommitData | null>(null)
  const [showDetails, setShowDetails] = useState(false)

  // Load GitHub data
  useEffect(() => {
    const loadGitHubData = async () => {
      setLoading(true)
      try {
        // In a real implementation, this would fetch from GitHub API
        // For now, we'll use mock data
        setTimeout(() => {
          setStats(generateMockGitHubData())
          setLoading(false)
        }, 1000)
      } catch (error) {
        console.error('Failed to load GitHub data:', error)
        setStats(generateMockGitHubData()) // Fallback to mock data
        setLoading(false)
      }
    }

    if (visible) {
      loadGitHubData()
    }
  }, [visible, githubUsername])

  const { scale } = useSpring({
    scale: visible ? 1 : 0,
    config: { tension: 300, friction: 30 }
  })

  if (!visible) return null

  return (
    <group>
      {/* 3D Calendar */}
      {stats && !showDetails && (
        <animated.group scale={scale as any}>
          <Calendar3D
            commits={stats.commits}
            position={position}
            onDayHover={setHoveredDay}
          />
          
          {/* Floating tooltip for hovered day */}
          {hoveredDay && (
            <Html
              position={[position[0] + 2, position[1] + 1, position[2]]}
              center
            >
              <Box
                sx={{
                  bgcolor: 'rgba(0, 0, 0, 0.9)',
                  p: 1,
                  borderRadius: 1,
                  border: '1px solid rgba(76, 175, 80, 0.3)',
                  minWidth: 150
                }}
              >
                <Typography variant="body2" color="white" fontWeight="bold">
                  {new Date(hoveredDay.date).toLocaleDateString('en-US', { 
                    weekday: 'long',
                    month: 'short', 
                    day: 'numeric' 
                  })}
                </Typography>
                <Typography variant="body2" color="#4CAF50">
                  {hoveredDay.count} {hoveredDay.count === 1 ? 'contribution' : 'contributions'}
                </Typography>
              </Box>
            </Html>
          )}
        </animated.group>
      )}

      {/* Detailed stats view */}
      {showDetails && stats && (
        <Html
          position={position}
          transform
          occlude
          center
        >
          <Box
            sx={{
              width: '600px',
              bgcolor: 'rgba(26, 26, 26, 0.95)',
              backdropFilter: 'blur(20px)',
              borderRadius: 4,
              p: 4,
              border: '1px solid rgba(76, 175, 80, 0.3)',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.8)',
            }}
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <GitHub sx={{ color: '#4CAF50', fontSize: 32, mr: 2 }} />
                <Box>
                  <Typography variant="h4" color="white" fontWeight="bold">
                    GitHub Activity
                  </Typography>
                  <Typography variant="subtitle1" color="rgba(255,255,255,0.7)">
                    @{githubUsername} • Past 12 months
                  </Typography>
                </Box>
              </Box>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <CircularProgress sx={{ color: '#4CAF50' }} />
                </Box>
              ) : (
                <>
                  <StatsDisplay stats={stats} />
                  
                  <Typography variant="body1" color="rgba(255,255,255,0.7)" mb={2}>
                    Most active on <strong style={{ color: '#4CAF50' }}>{stats.mostActiveDay}s</strong>
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                    <button
                      onClick={() => setShowDetails(false)}
                      style={{
                        background: 'rgba(76, 175, 80, 0.2)',
                        border: '1px solid #4CAF50',
                        color: '#4CAF50',
                        padding: '8px 16px',
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      View Calendar
                    </button>
                    <button
                      onClick={onClose}
                      style={{
                        background: 'transparent',
                        border: '1px solid rgba(255,255,255,0.3)',
                        color: 'white',
                        padding: '8px 16px',
                        borderRadius: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      Close
                    </button>
                  </Box>
                </>
              )}
            </motion.div>
          </Box>
        </Html>
      )}

      {/* Toggle button */}
      {stats && !loading && (
        <Html
          position={[position[0], position[1] - 1.5, position[2]]}
          center
        >
          <button
            onClick={() => setShowDetails(!showDetails)}
            style={{
              background: 'rgba(33, 150, 243, 0.2)',
              border: '1px solid #2196F3',
              color: '#2196F3',
              padding: '6px 12px',
              borderRadius: '20px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            {showDetails ? 'View Calendar' : 'View Stats'}
          </button>
        </Html>
      )}
    </group>
  )
}