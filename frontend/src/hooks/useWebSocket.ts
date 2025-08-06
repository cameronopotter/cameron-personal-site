import { useEffect, useState, useCallback, useRef } from 'react'
import { useGardenStore } from '@/stores/gardenStore'
import type { WebSocketMessage } from '@/types'

interface UseWebSocketReturn {
  connected: boolean
  lastMessage: string | null
  error: string | null
  reconnect: () => void
}

export const useWebSocket = (url?: string): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5
  
  const { updateRealtimeData, updateWeather, showNotification } = useGardenStore()
  
  // Default WebSocket URL (would be configured based on environment)
  const wsUrl = url || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`
  
  const connect = useCallback(() => {
    try {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        return
      }
      
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws
      
      ws.onopen = () => {
        setIsConnected(true)
        setError(null)
        reconnectAttempts.current = 0
        
        // Send initial connection message
        ws.send(JSON.stringify({
          type: 'visitor_joined',
          payload: {
            sessionId: useGardenStore.getState().visitorSession.id,
            timestamp: new Date().toISOString()
          }
        }))
        
        showNotification({
          type: 'success',
          message: 'Connected to garden network',
          duration: 3000,
          persistent: false
        })
      }
      
      ws.onmessage = (event) => {
        try {
          setLastMessage(event.data)
          const message: WebSocketMessage = JSON.parse(event.data)
          handleWebSocketMessage(message)
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }
      
      ws.onclose = (event) => {
        setIsConnected(false)
        wsRef.current = null
        
        if (!event.wasClean && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current += 1
            connect()
          }, delay)
        }
      }
      
      ws.onerror = (event) => {
        setError('WebSocket connection failed')
        console.error('WebSocket error:', event)
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown WebSocket error')
    }
  }, [wsUrl, showNotification])
  
  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'weather_update':
        updateWeather(message.payload)
        break
        
      case 'project_growth':
        updateRealtimeData({
          projectGrowthUpdates: [message.payload]
        })
        break
        
      case 'visitor_joined':
        updateRealtimeData({
          activeVisitors: message.payload.activeVisitors
        })
        break
        
      case 'visitor_left':
        updateRealtimeData({
          activeVisitors: message.payload.activeVisitors
        })
        break
        
      case 'interaction':
        updateRealtimeData({
          recentInteractions: [message.payload, ...useGardenStore.getState().realtimeData.recentInteractions.slice(0, 9)]
        })
        break
        
      default:
        console.log('Unknown WebSocket message type:', message.type)
    }
  }, [updateWeather, updateRealtimeData])
  
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Component unmounting')
      wsRef.current = null
    }
    
    setIsConnected(false)
  }, [])
  
  const reconnect = useCallback(() => {
    disconnect()
    reconnectAttempts.current = 0
    connect()
  }, [connect, disconnect])
  
  // Initialize connection
  useEffect(() => {
    // Only connect in production or when explicitly enabled
    if (import.meta.env.PROD || import.meta.env.VITE_ENABLE_WEBSOCKET === 'true') {
      connect()
    }
    
    return disconnect
  }, [connect, disconnect])
  
  // Send heartbeat to keep connection alive
  useEffect(() => {
    if (isConnected && wsRef.current) {
      const heartbeatInterval = setInterval(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({
            type: 'heartbeat',
            payload: { timestamp: new Date().toISOString() }
          }))
        }
      }, 30000) // 30 second heartbeat
      
      return () => clearInterval(heartbeatInterval)
    }
  }, [isConnected])
  
  return {
    connected: isConnected,
    lastMessage,
    error,
    reconnect
  }
}