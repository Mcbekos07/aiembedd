from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix='/ws', tags=['ws-ai'])


@router.websocket('/ai/{project_id}')
async def ai_ws(websocket: WebSocket, project_id: int) -> None:
    await websocket.accept()
    await websocket.send_json({'type': 'ai', 'project_id': project_id, 'message': 'AI канал подключен'})
    try:
        while True:
            payload = await websocket.receive_text()
            await websocket.send_json({'type': 'ai', 'payload': payload})
    except WebSocketDisconnect:
        return
