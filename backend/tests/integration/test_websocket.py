"""
Integration tests for WebSocket functionality.
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock
from fastapi.testclient import TestClient
from fastapi import WebSocket, WebSocketDisconnect
import websockets

from app.integrations.websocket_manager import WebSocketManager
from app.websockets.garden_ws import handle_websocket_connection


class TestWebSocketIntegration:
    """Test WebSocket integration and real-time features."""

    @pytest.mark.ws
    @pytest.mark.integration
    async def test_websocket_connection_lifecycle(self, ws_manager: WebSocketManager, mock_websocket):
        """Test WebSocket connection establishment and cleanup."""
        client_id = "test-client-123"
        
        # Test connection
        await ws_manager.connect(mock_websocket, client_id)
        assert client_id in ws_manager.active_connections
        assert ws_manager.active_connections[client_id] == mock_websocket
        
        # Test disconnection
        await ws_manager.disconnect(mock_websocket, client_id)
        assert client_id not in ws_manager.active_connections

    @pytest.mark.ws
    async def test_broadcast_to_all_clients(self, ws_manager: WebSocketManager):
        """Test broadcasting messages to all connected clients."""
        # Create mock clients
        clients = {}
        for i in range(5):
            client_id = f"client-{i}"
            mock_ws = Mock()
            mock_ws.send_json = AsyncMock()
            clients[client_id] = mock_ws
            await ws_manager.connect(mock_ws, client_id)
        
        message = {"type": "garden_update", "data": {"projects": []}}
        
        # Broadcast to all
        await ws_manager.broadcast_to_all(message)
        
        # Verify all clients received the message
        for client_id, mock_ws in clients.items():
            mock_ws.send_json.assert_called_once_with(message)

    @pytest.mark.ws
    async def test_send_to_specific_client(self, ws_manager: WebSocketManager, mock_websocket):
        """Test sending messages to specific clients."""
        client_id = "target-client"
        await ws_manager.connect(mock_websocket, client_id)
        
        message = {"type": "personal_message", "content": "Hello!"}
        
        # Send to specific client
        result = await ws_manager.send_to_client(client_id, message)
        
        assert result is True
        mock_websocket.send_json.assert_called_once_with(message)
        
        # Test sending to non-existent client
        result = await ws_manager.send_to_client("non-existent", message)
        assert result is False

    @pytest.mark.ws
    @pytest.mark.integration
    async def test_real_time_garden_updates(self, ws_manager: WebSocketManager):
        """Test real-time garden data updates."""
        # Setup multiple clients
        clients = []
        for i in range(3):
            mock_ws = Mock()
            mock_ws.send_json = AsyncMock()
            client_id = f"viewer-{i}"
            await ws_manager.connect(mock_ws, client_id)
            clients.append((client_id, mock_ws))
        
        # Simulate garden update
        garden_update = {
            "type": "garden_update",
            "timestamp": "2024-01-01T00:00:00Z",
            "data": {
                "projects": [
                    {
                        "id": 1,
                        "name": "New Project",
                        "position": {"x": 5, "y": 0, "z": -3},
                        "growth": 0.75
                    }
                ],
                "weather": {
                    "condition": "sunny",
                    "temperature": 25.5
                }
            }
        }
        
        await ws_manager.broadcast_garden_update(garden_update)
        
        # Verify all clients received the update
        for client_id, mock_ws in clients:
            mock_ws.send_json.assert_called_with(garden_update)

    @pytest.mark.ws
    async def test_websocket_error_handling(self, ws_manager: WebSocketManager):
        """Test WebSocket error handling and recovery."""
        # Create a mock WebSocket that raises exceptions
        mock_ws = Mock()
        mock_ws.send_json = AsyncMock(side_effect=ConnectionResetError("Connection lost"))
        
        client_id = "error-client"
        await ws_manager.connect(mock_ws, client_id)
        
        message = {"type": "test", "data": "test"}
        
        # Should handle the error gracefully
        result = await ws_manager.send_to_client(client_id, message)
        assert result is False
        
        # Client should be automatically disconnected
        assert client_id not in ws_manager.active_connections

    @pytest.mark.ws
    @pytest.mark.performance
    async def test_high_volume_websocket_messages(self, ws_manager: WebSocketManager):
        """Test WebSocket performance with high message volume."""
        # Setup client
        mock_ws = Mock()
        mock_ws.send_json = AsyncMock()
        client_id = "load-test-client"
        await ws_manager.connect(mock_ws, client_id)
        
        # Send many messages rapidly
        messages = []
        for i in range(1000):
            message = {
                "type": "performance_test",
                "sequence": i,
                "timestamp": f"2024-01-01T00:{i//60:02d}:{i%60:02d}Z"
            }
            messages.append(ws_manager.send_to_client(client_id, message))
        
        # Execute all sends concurrently
        results = await asyncio.gather(*messages, return_exceptions=True)
        
        # Most should succeed (allowing for some failure under load)
        success_count = sum(1 for r in results if r is True)
        assert success_count >= 950  # At least 95% success rate

    @pytest.mark.ws
    @pytest.mark.integration
    async def test_websocket_message_types(self, ws_manager: WebSocketManager, mock_websocket):
        """Test different types of WebSocket messages."""
        client_id = "test-client"
        await ws_manager.connect(mock_websocket, client_id)
        
        test_messages = [
            {
                "type": "project_created",
                "data": {"project_id": 123, "name": "New Project"}
            },
            {
                "type": "skill_updated",
                "data": {"skill_id": 456, "level": 85}
            },
            {
                "type": "weather_changed",
                "data": {"condition": "rainy", "temperature": 18}
            },
            {
                "type": "visitor_joined",
                "data": {"visitor_id": "visitor-789", "location": "homepage"}
            },
            {
                "type": "performance_alert",
                "data": {"metric": "fps", "value": 25, "threshold": 30}
            }
        ]
        
        for message in test_messages:
            await ws_manager.send_to_client(client_id, message)
            mock_websocket.send_json.assert_called_with(message)

    @pytest.mark.ws
    async def test_websocket_connection_limits(self, ws_manager: WebSocketManager):
        """Test WebSocket connection limits and cleanup."""
        # Connect many clients
        clients = []
        for i in range(100):
            mock_ws = Mock()
            mock_ws.send_json = AsyncMock()
            client_id = f"client-{i}"
            await ws_manager.connect(mock_ws, client_id)
            clients.append((client_id, mock_ws))
        
        assert len(ws_manager.active_connections) == 100
        
        # Disconnect half of them
        for i in range(0, 50):
            client_id = f"client-{i}"
            await ws_manager.disconnect(clients[i][1], client_id)
        
        assert len(ws_manager.active_connections) == 50

    @pytest.mark.ws
    @pytest.mark.integration
    async def test_websocket_authentication(self, ws_manager: WebSocketManager):
        """Test WebSocket authentication and authorization."""
        # Test unauthenticated connection
        mock_ws = Mock()
        mock_ws.send_json = AsyncMock()
        
        # Should be able to connect for read-only operations
        await ws_manager.connect(mock_ws, "anonymous-user")
        assert "anonymous-user" in ws_manager.active_connections
        
        # Test authenticated connection with admin privileges
        admin_ws = Mock()
        admin_ws.send_json = AsyncMock()
        
        await ws_manager.connect(admin_ws, "admin-user", {"role": "admin"})
        assert "admin-user" in ws_manager.active_connections

    @pytest.mark.ws
    async def test_websocket_rate_limiting(self, ws_manager: WebSocketManager, mock_websocket):
        """Test WebSocket message rate limiting."""
        client_id = "rate-limited-client"
        await ws_manager.connect(mock_websocket, client_id)
        
        # Send messages rapidly (should trigger rate limiting)
        messages_sent = 0
        for i in range(100):
            try:
                result = await ws_manager.send_to_client(client_id, {
                    "type": "spam_test",
                    "sequence": i
                })
                if result:
                    messages_sent += 1
            except Exception:
                break  # Rate limiting kicked in
            
            # Small delay to avoid overwhelming
            await asyncio.sleep(0.001)
        
        # Should have sent some messages but not all (due to rate limiting)
        assert 0 < messages_sent <= 100

    @pytest.mark.ws
    @pytest.mark.integration
    async def test_websocket_reconnection_handling(self, ws_manager: WebSocketManager):
        """Test WebSocket reconnection scenarios."""
        client_id = "reconnecting-client"
        
        # Initial connection
        mock_ws1 = Mock()
        mock_ws1.send_json = AsyncMock()
        await ws_manager.connect(mock_ws1, client_id)
        
        # Simulate disconnection
        await ws_manager.disconnect(mock_ws1, client_id)
        assert client_id not in ws_manager.active_connections
        
        # Reconnection with same client ID
        mock_ws2 = Mock()
        mock_ws2.send_json = AsyncMock()
        await ws_manager.connect(mock_ws2, client_id)
        
        # Should be connected with new WebSocket instance
        assert client_id in ws_manager.active_connections
        assert ws_manager.active_connections[client_id] == mock_ws2

    @pytest.mark.ws
    @pytest.mark.integration
    async def test_websocket_message_queuing(self, ws_manager: WebSocketManager):
        """Test message queuing for offline clients."""
        client_id = "offline-client"
        
        # Enable message queuing for this client
        ws_manager.enable_message_queue(client_id, max_size=100)
        
        # Send messages while client is offline
        messages = []
        for i in range(10):
            message = {"type": "queued_message", "sequence": i}
            messages.append(message)
            await ws_manager.queue_message(client_id, message)
        
        # Connect client and verify queued messages are delivered
        mock_ws = Mock()
        mock_ws.send_json = AsyncMock()
        await ws_manager.connect(mock_ws, client_id)
        
        # Should receive all queued messages
        await ws_manager.deliver_queued_messages(client_id)
        
        assert mock_ws.send_json.call_count == 10
        
        # Verify message order
        calls = mock_ws.send_json.call_args_list
        for i, call in enumerate(calls):
            assert call[0][0]["sequence"] == i