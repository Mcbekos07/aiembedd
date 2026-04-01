from app.services.git.git_service import GitService


class GitBranchService(GitService):
    def current_branch(self, repo_path: str) -> str:
        return self.run(repo_path, ['rev-parse', '--abbrev-ref', 'HEAD'])

    def list_branches(self, repo_path: str) -> list[str]:
        output = self.run(repo_path, ['branch'])
        return [line.replace('*', '').strip() for line in output.splitlines() if line.strip()]

    def switch_branch(self, repo_path: str, branch_name: str) -> str:
        return self.run(repo_path, ['checkout', branch_name])
