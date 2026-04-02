from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.ai_patch import PatchActionResponse, PatchApplyRequest, PatchProposalRequest
from app.services.ai.ai_action_service import AIActionService
from app.services.ai.ai_patch_service import AIPatchService
from app.services.ai.policies.action_policy import ActionPolicy

router = APIRouter(prefix='/ai-agent', tags=['ai-agent'])


class AgentActionRequest(BaseModel):
    action: str
    payload: str


@router.post('/act')
def run_action(payload: AgentActionRequest) -> dict[str, str]:
    if not ActionPolicy().validate(payload.action):
        raise HTTPException(status_code=400, detail='Недопустимое действие')

    output = AIActionService().run(payload.action, payload.payload)
    return {'status': 'ok', 'result': output}


@router.get('/patches/{project_id}')
def list_patches(project_id: int, db: Session = Depends(get_db_session)) -> dict[str, object]:
    rows = AIPatchService(db).list_by_project(project_id)
    items = [
        {
            'id': row.id,
            'status': row.status,
            'reason': row.reason,
            'summary': row.summary,
            'dangerous': row.dangerous == 'yes',
            'files': [item['path'] for item in row.changes],
            'diff_preview': row.diff_preview,
            'git_status_after_apply': row.git_status_after_apply,
        }
        for row in rows
    ]
    return {'status': 'ok', 'items': items}


@router.post('/patches/propose', response_model=PatchActionResponse)
def propose_patch(payload: PatchProposalRequest, db: Session = Depends(get_db_session)) -> PatchActionResponse:
    try:
        row = AIPatchService(db).propose(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PatchActionResponse(
        patch_id=row.id,
        status=row.status,
        diff_preview=row.diff_preview,
        files=[item['path'] for item in row.changes],
    )


@router.post('/patches/{patch_id}/apply', response_model=PatchActionResponse)
def apply_patch(patch_id: int, payload: PatchApplyRequest, db: Session = Depends(get_db_session)) -> PatchActionResponse:
    try:
        row = AIPatchService(db).apply(patch_id, confirmed=payload.confirmed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PatchActionResponse(
        patch_id=row.id,
        status=row.status,
        diff_preview=row.diff_preview,
        files=[item['path'] for item in row.changes],
        git_status=row.git_status_after_apply,
    )


@router.post('/patches/{patch_id}/reject', response_model=PatchActionResponse)
def reject_patch(patch_id: int, db: Session = Depends(get_db_session)) -> PatchActionResponse:
    try:
        row = AIPatchService(db).reject(patch_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PatchActionResponse(
        patch_id=row.id,
        status=row.status,
        diff_preview=row.diff_preview,
        files=[item['path'] for item in row.changes],
    )


@router.post('/patches/{patch_id}/rollback', response_model=PatchActionResponse)
def rollback_patch(patch_id: int, db: Session = Depends(get_db_session)) -> PatchActionResponse:
    try:
        row = AIPatchService(db).rollback(patch_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PatchActionResponse(
        patch_id=row.id,
        status=row.status,
        diff_preview=row.diff_preview,
        files=[item['path'] for item in row.changes],
    )
