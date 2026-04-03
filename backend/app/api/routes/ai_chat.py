from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.ai.ai_chat_service import AIChatService
from app.services.project.project_service import ProjectService

router = APIRouter(prefix='/ai-chat', tags=['ai-chat'])


class ChatRequest(BaseModel):
    content: str
    mode: str = 'quick_diagnosis'


@router.get('/{project_id}')
def list_chat(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, list[dict[str, str]]]:
    rows = AIChatService(db).list_messages(project_id)
    return {'status': 'ok', 'items': [{'role': r.role, 'content': r.content, 'created_at': r.created_at.isoformat()} for r in rows]}


@router.post('/{project_id}')
def send_chat(project_id: int, payload: ChatRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    project = ProjectService(db).get_project_by_id(project_id)
    msg = AIChatService(db).send(project, payload.content, mode=payload.mode)
    return {'status': 'ok', 'reply': msg.content}
