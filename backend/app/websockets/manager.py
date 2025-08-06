"""
WebSocket connection manager for real-time garden updates
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime
from uuid import UUID

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time garden updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_info: Dict[str, Any] = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Store connection metadata
        self.connection_info[websocket] = {
            "connected_at": datetime.utcnow(),
            "client_info": client_info or {},
            "subscriptions": set()
        }
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "message": "Welcome to Digital Greenhouse real-time updates",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if websocket in self.connection_info:
            del self.connection_info[websocket]
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any], subscription_filter: Optional[str] = None):
        """Broadcast message to all connected clients or filtered subset"""
        
        # Add timestamp to message
        message["timestamp"] = datetime.utcnow().isoformat()
        
        disconnected_connections = []
        
        for connection in self.active_connections:
            try:
                # Check subscription filter
                if subscription_filter:
                    subscriptions = self.connection_info.get(connection, {}).get("subscriptions", set())
                    if subscription_filter not in subscriptions:
                        continue
                
                await connection.send_text(json.dumps(message, default=str))
                
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected_connections.append(connection)
        
        # Clean up failed connections
        for connection in disconnected_connections:
            self.disconnect(connection)
        
        logger.debug(f"Broadcast message sent to {len(self.active_connections) - len(disconnected_connections)} connections")
    
    async def subscribe(self, websocket: WebSocket, subscription: str):
        """Subscribe connection to specific event types"""
        if websocket in self.connection_info:
            self.connection_info[websocket]["subscriptions"].add(subscription)
            
            await self.send_personal_message({
                "type": "subscription_confirmed",
                "subscription": subscription,
                "message": f"Subscribed to {subscription} updates"
            }, websocket)
    
    async def unsubscribe(self, websocket: WebSocket, subscription: str):
        """Unsubscribe connection from specific event types"""
        if websocket in self.connection_info:
            self.connection_info[websocket]["subscriptions"].discard(subscription)
            
            await self.send_personal_message({
                "type": "subscription_removed",
                "subscription": subscription,
                "message": f"Unsubscribed from {subscription} updates"
            }, websocket)
    
    async def broadcast_project_growth(self, project_id: UUID, growth_data: Dict[str, Any]):
        """Broadcast when a project grows to a new stage"""
        message = {
            "type": "project_growth",
            "event": "growth_stage_changed",
            "project_id": str(project_id),
            "data": growth_data
        }
        
        await self.broadcast(message, "project_updates")
        logger.info(f"Broadcast project growth: {project_id} -> {growth_data.get('new_stage')}")
    
    async def broadcast_weather_change(self, weather_data: Dict[str, Any]):
        """Notify all clients of weather state changes"""
        message = {
            "type": "weather_change",
            "event": "weather_updated",
            "data": weather_data
        }
        
        await self.broadcast(message, "weather_updates")
        logger.info(f"Broadcast weather change: {weather_data.get('weather_type')}")
    
    async def broadcast_visitor_interaction(self, interaction_data: Dict[str, Any]):
        """Show real-time visitor interactions (anonymized)"""
        # Anonymize sensitive data
        safe_interaction = {
            "interaction_type": interaction_data.get("interaction_type"),
            "project_id": interaction_data.get("project_id"),
            "timestamp": interaction_data.get("timestamp"),
            "visitor_hash": interaction_data.get("visitor_session", "")[:8] + "..."
        }
        
        message = {
            "type": "visitor_interaction",
            "event": "interaction_recorded",
            "data": safe_interaction
        }
        
        await self.broadcast(message, "visitor_activity")
        logger.debug(f"Broadcast visitor interaction: {safe_interaction['interaction_type']}")
    
    async def broadcast_seed_planted(self, seed_data: Dict[str, Any]):
        """Broadcast when a new seed is planted"""
        message = {
            "type": "seed_planted",
            "event": "new_project_seeded",
            "data": seed_data
        }
        
        await self.broadcast(message, "garden_changes")
        logger.info(f"Broadcast seed planted: {seed_data.get('project_name')}")
    
    async def broadcast_system_announcement(self, announcement: Dict[str, Any]):
        """Broadcast system-wide announcements"""
        message = {
            "type": "system_announcement",
            "event": "announcement",
            "data": announcement
        }
        
        await self.broadcast(message)  # No filter - send to all
        logger.info(f"Broadcast system announcement: {announcement.get('title')}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get current connection statistics"""
        total_connections = len(self.active_connections)
        
        # Count subscriptions
        subscription_counts = {}
        for conn_info in self.connection_info.values():
            for subscription in conn_info.get("subscriptions", set()):
                subscription_counts[subscription] = subscription_counts.get(subscription, 0) + 1
        
        return {
            "total_connections": total_connections,
            "subscription_counts": subscription_counts,
            "connection_details": [
                {
                    "connected_at": info["connected_at"].isoformat(),
                    "subscriptions": list(info["subscriptions"]),
                    "client_info": info["client_info"]
                }
                for info in self.connection_info.values()
            ]
        }


# Global WebSocket manager instance
websocket_manager = WebSocketManager()