from app.services.git.git_service import GitService


class GitCommitService(GitService):
    def commit_all(self, repo_path: str, message: str) -> str:
        self.run(repo_path, ['add', '.'])
        return self.run(repo_path, ['commit', '-m', message])
