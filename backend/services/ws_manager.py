"""
WebSocket manager for Star Citizen App.
Manages WebSocket connections and broadcasting messages to connected clients.
"""

from typing import List

from fastapi import WebSocket


class WSManager:
    """
    WebSocket connection manager.
    
    Maintains a list of active WebSocket connections and provides
    methods for connecting, disconnecting, and broadcasting messages.
    """
    
    def __init__(self):
        """Initialize WebSocket manager with empty connections list."""
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection to register
        """
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket) -> None:
        """
        Unregister a WebSocket connection.
        
        Args:
            websocket: WebSocket connection to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict) -> None:
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: Dictionary to send as JSON to all clients
            
        Note:
            Failed sends are silently ignored. Consider adding
            error handling and automatic disconnection for failed sends.
        """
        for websocket in self.active_connections:
            try:
                await websocket.send_json(message)
            except Exception:
                # Connection might be closed, will be cleaned up on next disconnect
                pass


# Global WebSocket manager instance
ws_manager = WSManager()