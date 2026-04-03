from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.ai.ai_memory_service import AIMemoryService

router = APIRouter(prefix='/ai-memory', tags=['ai-memory'])


class MemoryRequest(BaseModel):
    key: str
    value: str


class TypedMemoryRequest(BaseModel):
    memory_type: str
    title: str
    content: str
    importance: int = 3
    source: str = 'manual'


@router.get('/{project_id}')
def list_memory(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, object]:
    items = AIMemoryService(db).list_typed(project_id)
    return {'status': 'ok', 'items': items}


@router.get('/{project_id}/knowledge')
def memory_knowledge(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, object]:
    return {'status': 'ok', **AIMemoryService(db).summarize_by_type(project_id)}


@router.get('/{project_id}/active')
def active_memory(project_id: int, task_text: str = '', opened_file_path: str | None = None, limit: int = 10, db: Session = Depends(get_db_session)) -> dict[str, object]:
    items = AIMemoryService(db).get_active_memory_for_task(project_id, task_text=task_text, opened_file_path=opened_file_path, limit=limit)
    return {'status': 'ok', 'items': items}


@router.get('/{project_id}/warm')
def warm_memory(project_id: int, task_text: str = '', opened_file_path: str | None = None, limit: int = 20, db: Session = Depends(get_db_session)) -> dict[str, object]:
    items = AIMemoryService(db).get_relevant_warm_memory(project_id, task_text=task_text, opened_file_path=opened_file_path, limit=limit)
    return {'status': 'ok', 'items': items}


@router.get('/{project_id}/cold')
def cold_memory(project_id: int, task_text: str = '', opened_file_path: str | None = None, limit: int = 30, db: Session = Depends(get_db_session)) -> dict[str, object]:
    items = AIMemoryService(db).fetch_cold_memory(project_id, task_text=task_text, opened_file_path=opened_file_path, limit=limit)
    return {'status': 'ok', 'items': items}


@router.post('/{project_id}')
def add_memory(project_id: int, payload: MemoryRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    AIMemoryService(db).add(project_id, payload.key, payload.value)
    return {'status': 'ok', 'message': 'Запись памяти сохранена'}


@router.post('/{project_id}/typed')
def add_typed_memory(project_id: int, payload: TypedMemoryRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    AIMemoryService(db).add_typed(
        project_id,
        payload.memory_type,
        payload.title,
        payload.content,
        importance=payload.importance,
        source=payload.source,
    )
    return {'status': 'ok', 'message': 'Typed memory saved'}


@router.post('/{project_id}/maintenance/compact')
def compact_memory(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, object]:
    result = AIMemoryService(db).compact_old_data(project_id)
    return {'status': 'ok', **result}


@router.post('/{project_id}/maintenance/promote-history')
def promote_history(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, object]:
    promoted = AIMemoryService(db).promote_history_events(project_id)
    return {'status': 'ok', 'promoted': promoted}


@router.post('/{project_id}/maintenance/summarize')
def summarize_memory(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, object]:
    result = AIMemoryService(db).maintenance_summarize(project_id)
    return {'status': 'ok', **result}
