"""Import all ORM models so SQLAlchemy metadata is fully registered."""

from app.db.models.ai_agent_checkpoint import AIAgentCheckpoint
from app.db.models.ai_chat_message import AIChatMessage
from app.db.models.ai_memory_entry import AIMemoryEntry
from app.db.models.ai_patch_set import AIPatchSet
from app.db.models.ai_project_binding import AIProjectBinding
from app.db.models.ai_prompt_version import AIPromptVersion
from app.db.models.ai_provider import AIProvider
from app.db.models.ai_task import AITask
from app.db.models.ai_task_action import AITaskAction
from app.db.models.artifact import Artifact
from app.db.models.build_job import BuildJob
from app.db.models.dependency_state import DependencyState
from app.db.models.flash_job import FlashJob
from app.db.models.git_branch import GitBranch
from app.db.models.git_commit import GitCommit
from app.db.models.monitor_session import MonitorSession
from app.db.models.project import Project
from app.db.models.project_history import ProjectHistory
from app.db.models.project_knowledge_snapshot import ProjectKnowledgeSnapshot
from app.db.models.project_remote import ProjectRemote
from app.db.models.system_setting import SystemSetting
from app.db.models.toolchain_state import ToolchainState
from app.db.models.version import Version

__all__ = [
    'AIAgentCheckpoint',
    'AIChatMessage',
    'AIMemoryEntry',
    'AIPatchSet',
    'AIProjectBinding',
    'AIPromptVersion',
    'AIProvider',
    'AITask',
    'AITaskAction',
    'Artifact',
    'BuildJob',
    'DependencyState',
    'FlashJob',
    'GitBranch',
    'GitCommit',
    'MonitorSession',
    'Project',
    'ProjectHistory',
    'ProjectKnowledgeSnapshot',
    'ProjectRemote',
    'SystemSetting',
    'ToolchainState',
    'Version',
]
