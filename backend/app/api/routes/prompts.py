from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.prompts.prompt_service import PromptService
from app.services.prompts.prompt_version_service import PromptVersionService

router = APIRouter(prefix='/prompts', tags=['prompts'])


class PromptSaveRequest(BaseModel):
    prompt_text: str


@router.get('/{project_id}')
def get_prompt(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, str]:
    return {'status': 'ok', 'prompt_text': PromptService(db).get_current_prompt(project_id)}


@router.post('/{project_id}')
def save_prompt(project_id: int, payload: PromptSaveRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    row = PromptService(db).save_prompt(project_id, payload.prompt_text)
    return {'status': 'ok', 'version': row.version}


@router.get('/{project_id}/versions')
def list_prompt_versions(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, list[dict[str, str]]]:
    rows = PromptVersionService(db).list_versions(project_id)
    return {'status': 'ok', 'items': [{'version': r.version, 'created_at': r.created_at.isoformat()} for r in rows]}
