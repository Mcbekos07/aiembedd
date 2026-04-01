from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai.ai_action_service import AIActionService
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
