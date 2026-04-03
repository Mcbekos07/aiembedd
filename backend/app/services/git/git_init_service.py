from app.services.git.git_service import GitService


class GitInitService(GitService):
    def init_repo(self, repo_path: str) -> str:
        return self.run(repo_path, ['init'])
