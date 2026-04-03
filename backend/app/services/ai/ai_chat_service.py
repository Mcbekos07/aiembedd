from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai_chat_message import AIChatMessage
from app.db.models.ai_project_binding import AIProjectBinding
from app.db.models.project import Project
from app.services.ai.ai_context_service import AIContextService
from app.services.ai.ai_router_service import AIRouterService
from app.services.history.event_write_service import EventWriteService


class AIChatService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_messages(self, project_id: int) -> list[AIChatMessage]:
        stmt = select(AIChatMessage).where(AIChatMessage.project_id == project_id).order_by(AIChatMessage.created_at.asc())
        return list(self.db.scalars(stmt).all())

    def send(self, project: Project, content: str, mode: str = 'quick_diagnosis') -> AIChatMessage:
        self.db.add(AIChatMessage(project_id=project.id, role='user', content=content))
        binding = self.db.query(AIProjectBinding).filter(AIProjectBinding.project_id == project.id).first()
        provider = binding.provider if binding else project.ai_provider
        model = binding.model if binding else project.ai_model

        pipeline = AIContextService(self.db).build_context_with_report(project, content, mode=mode)
        context = str(pipeline['prompt_text'])
        answer = AIRouterService().route(provider, model, context)
        EventWriteService(self.db).write(project.id, 'context_pipeline_chat', 'Context pipeline assembled for chat', str(pipeline['report'])[:1200])

        assistant = AIChatMessage(project_id=project.id, role='assistant', content=answer)
        self.db.add(assistant)
        self.db.commit()
        self.db.refresh(assistant)
        return assistant
