from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix='/ws', tags=['ws-devices'])


@router.websocket('/devices')
async def devices_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({'type': 'devices', 'message': 'Канал устройств подключен'})
    try:
        while True:
            payload = await websocket.receive_text()
            await websocket.send_json({'type': 'devices', 'payload': payload})
    except WebSocketDisconnect:
        return
