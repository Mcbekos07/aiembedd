from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix='/ws', tags=['ws-monitor'])


@router.websocket('/monitor/{project_id}')
async def monitor_ws(websocket: WebSocket, project_id: int) -> None:
    await websocket.accept()
    await websocket.send_json({'type': 'monitor', 'project_id': project_id, 'message': 'Serial monitor канал подключен'})
    try:
        while True:
            payload = await websocket.receive_text()
            await websocket.send_json({'type': 'monitor', 'payload': payload})
    except WebSocketDisconnect:
        return
