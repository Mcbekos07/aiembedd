"""Dispatches validated AI actions to dedicated services."""

from app.services.ai.ai_build_assist_service import AIBuildAssistService
from app.services.ai.ai_code_action_service import AICodeActionService
from app.services.ai.ai_dependency_assist_service import AIDependencyAssistService
from app.services.ai.ai_diff_review_service import AIDiffReviewService
from app.services.ai.ai_version_assist_service import AIVersionAssistService


class AIActionService:
    def __init__(self) -> None:
        code = AICodeActionService()
        self._dispatch = {
            'suggest_code': code.suggest_code,
            'generate_patch': code.generate_patch,
            'review_diff': AIDiffReviewService().review,
            'explain_build_error': AIBuildAssistService().explain_error,
            'create_version_message': AIVersionAssistService().create_message,
            'dependency_install_plan': AIDependencyAssistService().install_plan,
        }

    def run(self, action: str, payload: str) -> str:
        return self._dispatch[action](payload)
