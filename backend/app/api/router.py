"""Top-level API router."""

from fastapi import APIRouter

from app.api.routes.ai_agent import router as ai_agent_router
from app.api.routes.ai_chat import router as ai_chat_router
from app.api.routes.ai_context_sources import router as ai_context_sources_router
from app.api.routes.ai_memory import router as ai_memory_router
from app.api.routes.ai_tasks import router as ai_tasks_router
from app.api.routes.branches import router as branches_router
from app.api.routes.builds import router as builds_router
from app.api.routes.dependencies import router as dependencies_router
from app.api.routes.devices import router as devices_router
from app.api.routes.environment import router as environment_router
from app.api.routes.files import router as files_router
from app.api.routes.flash import router as flash_router
from app.api.routes.git import router as git_router
from app.api.routes.health import router as health_router
from app.api.routes.history import router as history_router
from app.api.routes.logs import router as logs_router
from app.api.routes.monitor import router as monitor_router
from app.api.routes.projects import router as projects_router
from app.api.routes.prompts import router as prompts_router
from app.api.routes.remote_git import router as remote_git_router
from app.api.routes.settings import router as settings_router
from app.api.routes.system import router as system_router
from app.api.routes.toolchains import router as toolchains_router
from app.api.routes.versions import router as versions_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(system_router)
api_router.include_router(projects_router)
api_router.include_router(settings_router)
api_router.include_router(git_router)
api_router.include_router(branches_router)
api_router.include_router(versions_router)
api_router.include_router(history_router)
api_router.include_router(remote_git_router)
api_router.include_router(builds_router)
api_router.include_router(flash_router)
api_router.include_router(monitor_router)
api_router.include_router(logs_router)
api_router.include_router(devices_router)
api_router.include_router(dependencies_router)
api_router.include_router(toolchains_router)
api_router.include_router(environment_router)
api_router.include_router(files_router)
api_router.include_router(prompts_router)
api_router.include_router(ai_chat_router)
api_router.include_router(ai_context_sources_router)
api_router.include_router(ai_agent_router)
api_router.include_router(ai_memory_router)
api_router.include_router(ai_tasks_router)
