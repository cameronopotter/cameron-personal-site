"""
Garden WebSocket endpoints for real-time updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import json
import logging

from .manager import websocket_manager
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/garden")
async def garden_websocket_endpoint(
    websocket: WebSocket,
    visitor_session: Optional[str] = Query(None),
    client_type: Optional[str] = Query("web")
):
    """
    Main garden WebSocket endpoint for real-time updates
    
    Supports the following message types:
    - project_growth: Project growth stage changes
    - weather_change: Garden weather updates
    - visitor_interaction: Live visitor interactions
    - seed_planted: New project seeds
    - system_announcement: System-wide messages
    """
    
    if not settings.enable_websockets:
        await websocket.close(code=4000, reason="WebSockets are disabled")
        return
    
    client_info = {
        "visitor_session": visitor_session,
        "client_type": client_type
    }
    
    await websocket_manager.connect(websocket, client_info)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_client_message(websocket, message)
                
            except json.JSONDecodeError:
                await websocket_manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
                
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket_manager.send_personal_message({
                    "type": "error", 
                    "message": "Error processing message"
                }, websocket)
    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
        websocket_manager.disconnect(websocket)
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


async def handle_client_message(websocket: WebSocket, message: dict):
    """Handle incoming messages from WebSocket clients"""
    
    message_type = message.get("type")
    
    if message_type == "subscribe":
        # Client wants to subscribe to specific event types
        subscription = message.get("subscription")
        if subscription:
            await websocket_manager.subscribe(websocket, subscription)
        
    elif message_type == "unsubscribe":
        # Client wants to unsubscribe from event types
        subscription = message.get("subscription")
        if subscription:
            await websocket_manager.unsubscribe(websocket, subscription)
    
    elif message_type == "ping":
        # Heartbeat/keepalive
        await websocket_manager.send_personal_message({
            "type": "pong",
            "timestamp": message.get("timestamp")
        }, websocket)
    
    elif message_type == "get_stats":
        # Client requesting connection stats (admin only)
        stats = websocket_manager.get_connection_stats()
        await websocket_manager.send_personal_message({
            "type": "connection_stats",
            "data": stats
        }, websocket)
    
    else:
        await websocket_manager.send_personal_message({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }, websocket)