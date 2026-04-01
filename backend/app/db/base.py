"""SQLAlchemy base metadata and model imports."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base model class for ORM entities."""


from app.db.models.ai_chat_message import AIChatMessage  # noqa: E402,F401
from app.db.models.ai_memory_entry import AIMemoryEntry  # noqa: E402,F401
from app.db.models.ai_project_binding import AIProjectBinding  # noqa: E402,F401
from app.db.models.ai_prompt_version import AIPromptVersion  # noqa: E402,F401
from app.db.models.ai_provider import AIProvider  # noqa: E402,F401
from app.db.models.ai_task import AITask  # noqa: E402,F401
from app.db.models.ai_task_action import AITaskAction  # noqa: E402,F401
from app.db.models.artifact import Artifact  # noqa: E402,F401
from app.db.models.build_job import BuildJob  # noqa: E402,F401
from app.db.models.dependency_state import DependencyState  # noqa: E402,F401
from app.db.models.flash_job import FlashJob  # noqa: E402,F401
from app.db.models.git_branch import GitBranch  # noqa: E402,F401
from app.db.models.git_commit import GitCommit  # noqa: E402,F401
from app.db.models.monitor_session import MonitorSession  # noqa: E402,F401
from app.db.models.project import Project  # noqa: E402,F401
from app.db.models.project_history import ProjectHistory  # noqa: E402,F401
from app.db.models.project_remote import ProjectRemote  # noqa: E402,F401
from app.db.models.system_setting import SystemSetting  # noqa: E402,F401
from app.db.models.toolchain_state import ToolchainState  # noqa: E402,F401
from app.db.models.version import Version  # noqa: E402,F401
