from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix='/ws', tags=['ws-logs'])


@router.websocket('/logs/{project_id}')
async def logs_ws(websocket: WebSocket, project_id: int) -> None:
    await websocket.accept()
    await websocket.send_json({'type': 'log', 'project_id': project_id, 'message': 'Канал логов подключен'})
    try:
        while True:
            payload = await websocket.receive_text()
            await websocket.send_json({'type': 'log', 'payload': payload})
    except WebSocketDisconnect:
        return
