from app.services.git.git_service import GitService


class GitTagService(GitService):
    def create_tag(self, repo_path: str, tag_name: str) -> str:
        return self.run(repo_path, ['tag', tag_name])
