from app.services.git.git_service import GitService


class GitDiffService(GitService):
    def diff(self, repo_path: str) -> str:
        return self.run(repo_path, ['diff'])
