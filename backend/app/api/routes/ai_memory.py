from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.ai.ai_memory_service import AIMemoryService

router = APIRouter(prefix='/ai-memory', tags=['ai-memory'])


class MemoryRequest(BaseModel):
    key: str
    value: str


@router.get('/{project_id}')
def list_memory(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, list[dict[str, str]]]:
    rows = AIMemoryService(db).list(project_id)
    return {'status': 'ok', 'items': [{'key': r.key, 'value': r.value, 'created_at': r.created_at.isoformat()} for r in rows]}


@router.post('/{project_id}')
def add_memory(project_id: int, payload: MemoryRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    AIMemoryService(db).add(project_id, payload.key, payload.value)
    return {'status': 'ok', 'message': 'Запись памяти сохранена'}
