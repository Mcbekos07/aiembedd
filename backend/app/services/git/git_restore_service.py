from app.services.git.git_service import GitService


class GitRestoreService(GitService):
    def restore_path(self, repo_path: str, file_path: str) -> str:
        return self.run(repo_path, ['restore', file_path])
