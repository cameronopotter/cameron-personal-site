"""
WebSocket manager for real-time event broadcasting and connection handling.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .integration_config import integration_settings

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """WebSocket event types"""
    # Integration events
    COMMIT_PUSHED = "commit_pushed"
    MUSIC_CHANGED = "music_changed"
    WEATHER_UPDATED = "weather_updated"
    CODING_SESSION_START = "coding_session_start"
    CODING_SESSION_END = "coding_session_end"
    
    # Garden events
    GROWTH_STAGE_CHANGED = "growth_stage_changed"
    PLANT_BLOOMED = "plant_bloomed"
    ATMOSPHERE_CHANGED = "atmosphere_changed"
    
    # System events
    CONNECTION_STATUS = "connection_status"
    HEALTH_CHECK = "health_check"
    ERROR = "error"
    
    # Analytics events
    VISITOR_JOINED = "visitor_joined"
    VISITOR_LEFT = "visitor_left"
    INTERACTION_RECORDED = "interaction_recorded"


class ConnectionRole(str, Enum):
    """Connection role types"""
    VISITOR = "visitor"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class WebSocketEvent:
    """WebSocket event data structure"""
    type: EventType
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    target_roles: Optional[List[ConnectionRole]] = None
    target_connections: Optional[List[str]] = None
    event_id: str = None
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())


@dataclass 
class ConnectionInfo:
    """WebSocket connection information"""
    id: str
    websocket: WebSocket
    role: ConnectionRole
    connected_at: datetime
    last_ping: Optional[datetime]
    subscribed_events: Set[EventType]
    metadata: Dict[str, Any]
    is_active: bool = True


class EventQueue:
    """Event queue with filtering and rate limiting"""
    
    def __init__(self, max_size: int = 100, max_age_seconds: int = 300):
        self.max_size = max_size
        self.max_age_seconds = max_age_seconds
        self._queue: deque = deque(maxlen=max_size)
        self._event_counts: Dict[str, int] = defaultdict(int)
        self._last_cleanup = datetime.utcnow()
    
    def add_event(self, event: WebSocketEvent) -> bool:
        """Add event to queue with rate limiting"""
        now = datetime.utcnow()
        
        # Cleanup old events periodically
        if (now - self._last_cleanup).seconds > 60:
            self._cleanup_old_events()
        
        # Rate limiting: max 10 events per minute per type
        event_key = f"{event.type.value}_{event.source}"
        if self._event_counts[event_key] > 10:
            logger.warning(f"Rate limit exceeded for event type: {event.type}")
            return False
        
        self._queue.append(event)
        self._event_counts[event_key] += 1
        return True
    
    def get_recent_events(self, count: int = 10, event_types: Optional[Set[EventType]] = None) -> List[WebSocketEvent]:
        """Get recent events, optionally filtered by type"""
        events = list(self._queue)
        
        if event_types:
            events = [e for e in events if e.type in event_types]
        
        # Return most recent events
        return events[-count:] if events else []
    
    def _cleanup_old_events(self):
        """Remove old events and reset counters"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.max_age_seconds)
        
        # Remove old events
        while self._queue and self._queue[0].timestamp < cutoff:
            self._queue.popleft()
        
        # Reset event counters
        self._event_counts.clear()
        self._last_cleanup = now


class WebSocketManager:
    """WebSocket connection and event manager"""
    
    def __init__(self):
        self.connections: Dict[str, ConnectionInfo] = {}
        self.event_queue = EventQueue(
            max_size=integration_settings.websockets.max_queue_size,
            max_age_seconds=integration_settings.websockets.queue_timeout_seconds
        )
        self.event_handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._ping_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Configuration
        self.config = integration_settings.websockets
        self.max_connections = self.config.max_connections
        self.ping_interval = self.config.ping_interval
        self.ping_timeout = self.config.ping_timeout
        self.max_message_size = self.config.max_message_size
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        loop = asyncio.get_event_loop()
        self._ping_task = loop.create_task(self._ping_connections_loop())
        self._cleanup_task = loop.create_task(self._cleanup_connections_loop())
    
    async def connect(
        self, 
        websocket: WebSocket, 
        role: ConnectionRole = ConnectionRole.VISITOR,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Accept and register a new WebSocket connection"""
        
        # Check connection limit
        if len(self.connections) >= self.max_connections:
            await websocket.close(code=1013, reason="Too many connections")
            raise Exception("Maximum connections exceeded")
        
        # Accept connection
        await websocket.accept()
        
        # Generate connection ID
        connection_id = str(uuid.uuid4())
        
        # Determine default event subscriptions based on role
        if role == ConnectionRole.ADMIN:
            subscribed_events = set(EventType)  # Admin gets all events
        else:
            # Default events for visitors
            default_events = self.config.event_filters.get("default", [])
            subscribed_events = {
                EventType(event) for event in default_events 
                if event != "*" and event in [e.value for e in EventType]
            }
        
        # Create connection info
        connection_info = ConnectionInfo(
            id=connection_id,
            websocket=websocket,
            role=role,
            connected_at=datetime.utcnow(),
            last_ping=None,
            subscribed_events=subscribed_events,
            metadata=metadata or {},
            is_active=True
        )
        
        # Store connection
        self.connections[connection_id] = connection_info
        
        logger.info(f"WebSocket connection established: {connection_id} ({role.value})")
        
        # Send connection confirmation
        await self._send_to_connection(connection_id, {
            "type": EventType.CONNECTION_STATUS.value,
            "data": {
                "status": "connected",
                "connection_id": connection_id,
                "role": role.value,
                "subscribed_events": [e.value for e in subscribed_events]
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Broadcast visitor joined event (if not admin/system)
        if role == ConnectionRole.VISITOR:
            await self.broadcast_event(WebSocketEvent(
                type=EventType.VISITOR_JOINED,
                data={
                    "connection_id": connection_id,
                    "visitor_count": len([c for c in self.connections.values() if c.role == ConnectionRole.VISITOR])
                },
                timestamp=datetime.utcnow(),
                source="websocket_manager",
                target_roles=[ConnectionRole.ADMIN]
            ))
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Disconnect and clean up a WebSocket connection"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        connection.is_active = False
        
        try:
            await connection.websocket.close()
        except Exception as e:
            logger.warning(f"Error closing WebSocket {connection_id}: {e}")
        
        # Broadcast visitor left event (if visitor)
        if connection.role == ConnectionRole.VISITOR:
            await self.broadcast_event(WebSocketEvent(
                type=EventType.VISITOR_LEFT,
                data={
                    "connection_id": connection_id,
                    "session_duration": (datetime.utcnow() - connection.connected_at).total_seconds(),
                    "visitor_count": len([c for c in self.connections.values() if c.role == ConnectionRole.VISITOR and c.is_active]) - 1
                },
                timestamp=datetime.utcnow(),
                source="websocket_manager",
                target_roles=[ConnectionRole.ADMIN]
            ))
        
        # Remove connection
        del self.connections[connection_id]
        logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def broadcast_event(self, event: WebSocketEvent):
        """Broadcast event to appropriate connections"""
        
        # Add to event queue
        if not self.event_queue.add_event(event):
            logger.warning(f"Event dropped due to rate limiting: {event.type}")
            return
        
        # Determine target connections
        target_connections = []
        
        if event.target_connections:
            # Specific connections
            target_connections = [
                conn for conn_id, conn in self.connections.items()
                if conn_id in event.target_connections and conn.is_active
            ]
        else:
            # Filter by role and event subscriptions
            for connection in self.connections.values():
                if not connection.is_active:
                    continue
                
                # Check role filter
                if event.target_roles and connection.role not in event.target_roles:
                    continue
                
                # Check event subscription
                if event.type not in connection.subscribed_events:
                    continue
                
                target_connections.append(connection)
        
        # Send to target connections
        message = {
            "type": event.type.value,
            "data": event.data,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "event_id": event.event_id
        }
        
        disconnected_connections = []
        for connection in target_connections:
            try:
                await connection.websocket.send_text(json.dumps(message))
            except WebSocketDisconnect:
                disconnected_connections.append(connection.id)
            except Exception as e:
                logger.error(f"Error sending message to {connection.id}: {e}")
                disconnected_connections.append(connection.id)
        
        # Clean up disconnected connections
        for connection_id in disconnected_connections:
            await self.disconnect(connection_id)
        
        logger.debug(f"Broadcast event {event.type} to {len(target_connections)} connections")
    
    async def send_to_connection(self, connection_id: str, event: WebSocketEvent):
        """Send event to a specific connection"""
        event.target_connections = [connection_id]
        await self.broadcast_event(event)
    
    async def _send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Internal method to send raw message to connection"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        if not connection.is_active:
            return
        
        try:
            await connection.websocket.send_text(json.dumps(message))
        except WebSocketDisconnect:
            await self.disconnect(connection_id)
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            await self.disconnect(connection_id)
    
    async def handle_client_message(self, connection_id: str, message: str):
        """Handle message received from client"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "ping":
                # Respond to ping
                await self._send_to_connection(connection_id, {
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
                connection.last_ping = datetime.utcnow()
            
            elif message_type == "subscribe":
                # Update event subscriptions
                events = data.get("events", [])
                new_subscriptions = {EventType(e) for e in events if e in [ev.value for ev in EventType]}
                connection.subscribed_events.update(new_subscriptions)
                
                await self._send_to_connection(connection_id, {
                    "type": "subscription_updated",
                    "data": {"subscribed_events": [e.value for e in connection.subscribed_events]},
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif message_type == "unsubscribe":
                # Remove event subscriptions
                events = data.get("events", [])
                remove_subscriptions = {EventType(e) for e in events if e in [ev.value for ev in EventType]}
                connection.subscribed_events -= remove_subscriptions
                
                await self._send_to_connection(connection_id, {
                    "type": "subscription_updated",
                    "data": {"subscribed_events": [e.value for e in connection.subscribed_events]},
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif message_type == "get_recent_events":
                # Send recent events
                count = min(data.get("count", 10), 50)  # Limit to 50
                recent_events = self.event_queue.get_recent_events(
                    count=count,
                    event_types=connection.subscribed_events
                )
                
                await self._send_to_connection(connection_id, {
                    "type": "recent_events",
                    "data": {
                        "events": [
                            {
                                "type": e.type.value,
                                "data": e.data,
                                "timestamp": e.timestamp.isoformat(),
                                "source": e.source
                            }
                            for e in recent_events
                        ]
                    },
                    "timestamp": datetime.utcnow().isoformat()
                })
            
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from connection {connection_id}")
        except Exception as e:
            logger.error(f"Error handling client message from {connection_id}: {e}")
    
    async def _ping_connections_loop(self):
        """Background task to ping connections periodically"""
        while True:
            try:
                await asyncio.sleep(self.ping_interval)
                
                current_time = datetime.utcnow()
                timeout_connections = []
                
                for connection_id, connection in self.connections.items():
                    if not connection.is_active:
                        continue
                    
                    # Check for timeout
                    if (connection.last_ping and 
                        (current_time - connection.last_ping).seconds > self.ping_timeout * 2):
                        timeout_connections.append(connection_id)
                        continue
                    
                    # Send ping
                    try:
                        await connection.websocket.ping()
                    except Exception as e:
                        logger.warning(f"Ping failed for connection {connection_id}: {e}")
                        timeout_connections.append(connection_id)
                
                # Clean up timed out connections
                for connection_id in timeout_connections:
                    await self.disconnect(connection_id)
                
            except Exception as e:
                logger.error(f"Error in ping loop: {e}")
    
    async def _cleanup_connections_loop(self):
        """Background task to clean up stale connections"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                current_time = datetime.utcnow()
                stale_connections = []
                
                for connection_id, connection in self.connections.items():
                    # Remove connections inactive for more than 1 hour
                    if ((current_time - connection.connected_at).seconds > 3600 and
                        not connection.is_active):
                        stale_connections.append(connection_id)
                
                for connection_id in stale_connections:
                    if connection_id in self.connections:
                        del self.connections[connection_id]
                        logger.info(f"Cleaned up stale connection: {connection_id}")
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    def register_event_handler(self, event_type: EventType, handler: Callable[[WebSocketEvent], None]):
        """Register an event handler for specific event types"""
        self.event_handlers[event_type].append(handler)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        active_connections = [c for c in self.connections.values() if c.is_active]
        
        role_counts = defaultdict(int)
        for connection in active_connections:
            role_counts[connection.role.value] += 1
        
        return {
            "total_connections": len(active_connections),
            "connections_by_role": dict(role_counts),
            "max_connections": self.max_connections,
            "recent_events_count": len(self.event_queue._queue),
            "uptime_seconds": (datetime.utcnow() - datetime.utcnow()).total_seconds()  # Would track actual start time
        }
    
    async def shutdown(self):
        """Gracefully shutdown the WebSocket manager"""
        logger.info("Shutting down WebSocket manager...")
        
        # Cancel background tasks
        if self._ping_task:
            self._ping_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Close all connections
        close_tasks = []
        for connection_id in list(self.connections.keys()):
            close_tasks.append(self.disconnect(connection_id))
        
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
        
        logger.info("WebSocket manager shutdown complete")


# Global WebSocket manager instance
websocket_manager = WebSocketManager()