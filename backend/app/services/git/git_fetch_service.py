from app.services.git.git_service import GitService


class GitFetchService(GitService):
    def fetch(self, repo_path: str, remote: str = 'origin') -> str:
        return self.run(repo_path, ['fetch', remote])
