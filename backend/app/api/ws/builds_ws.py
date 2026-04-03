from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix='/ws', tags=['ws-builds'])


@router.websocket('/builds/{project_id}')
async def builds_ws(websocket: WebSocket, project_id: int) -> None:
    await websocket.accept()
    await websocket.send_json({'type': 'status', 'project_id': project_id, 'message': 'Канал build статусов подключен'})
    try:
        while True:
            payload = await websocket.receive_text()
            await websocket.send_json({'type': 'echo', 'payload': payload})
    except WebSocketDisconnect:
        return
