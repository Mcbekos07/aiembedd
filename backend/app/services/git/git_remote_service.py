from app.services.git.git_service import GitService


class GitRemoteService(GitService):
    def list_remotes(self, repo_path: str) -> str:
        return self.run(repo_path, ['remote', '-v'])

    def add_remote(self, repo_path: str, name: str, url: str) -> str:
        return self.run(repo_path, ['remote', 'add', name, url])
