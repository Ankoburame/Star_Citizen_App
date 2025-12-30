"""
WebSocket API endpoint for Star Citizen App.
Provides real-time dashboard updates via WebSocket connection.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.ws_manager import ws_manager

router = APIRouter()


@router.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time dashboard updates.
    
    Maintains a persistent connection with the client and keeps it alive
    by listening for messages. When the connection is closed, it properly
    cleans up the connection from the manager.
    
    Args:
        websocket: WebSocket connection instance
        
    Note:
        The connection will remain open until the client disconnects
        or a network error occurs.
    """
    await ws_manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive by receiving messages
            await websocket.receive_text()
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)