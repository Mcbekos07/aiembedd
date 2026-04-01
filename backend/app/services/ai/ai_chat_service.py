from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai_chat_message import AIChatMessage
from app.db.models.ai_project_binding import AIProjectBinding
from app.db.models.project import Project
from app.services.ai.ai_context_service import AIContextService
from app.services.ai.ai_router_service import AIRouterService


class AIChatService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_messages(self, project_id: int) -> list[AIChatMessage]:
        stmt = select(AIChatMessage).where(AIChatMessage.project_id == project_id).order_by(AIChatMessage.created_at.asc())
        return list(self.db.scalars(stmt).all())

    def send(self, project: Project, content: str) -> AIChatMessage:
        self.db.add(AIChatMessage(project_id=project.id, role='user', content=content))
        binding = self.db.query(AIProjectBinding).filter(AIProjectBinding.project_id == project.id).first()
        provider = binding.provider if binding else project.ai_provider
        model = binding.model if binding else project.ai_model

        context = AIContextService(self.db).build_context(project, content)
        answer = AIRouterService().route(provider, model, context)

        assistant = AIChatMessage(project_id=project.id, role='assistant', content=answer)
        self.db.add(assistant)
        self.db.commit()
        self.db.refresh(assistant)
        return assistant
