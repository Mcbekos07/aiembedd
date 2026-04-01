from app.services.git.git_service import GitService


class GitPullService(GitService):
    def pull(self, repo_path: str, remote: str = 'origin', branch: str = 'main') -> str:
        return self.run(repo_path, ['pull', remote, branch])
