from pathlib import Path

import pytest

from app.services.ai.policies.action_policy import ActionPolicy
from app.services.files.file_service import FileService
from app.services.git.remote_policy_service import RemoteGitPolicyService


def test_file_service_forbids_project_root_delete(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        FileService().delete(str(tmp_path), '.')


def test_action_policy_has_explicit_boundaries() -> None:
    policy = ActionPolicy()
    assert policy.validate('suggest_code')
    assert policy.validate('generate_patch')
    assert not policy.validate('flash_firmware')


def test_remote_git_policy_blocks_local_urls() -> None:
    policy = RemoteGitPolicyService()
    with pytest.raises(ValueError):
        policy.validate_remote_url('https://127.0.0.1/repo.git')
