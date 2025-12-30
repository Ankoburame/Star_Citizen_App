from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.ws_manager import ws_manager

router = APIRouter()

@router.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
