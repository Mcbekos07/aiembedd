"""Policy hooks for validating remote Git actions."""

from urllib.parse import urlparse


class RemoteGitPolicyService:
    """Applies conservative validation for remote and destination identifiers."""

    ALLOWED_SCHEMES = {'https', 'ssh', 'git'}
    BLOCKED_HOSTS = {'localhost', '127.0.0.1', '0.0.0.0'}

    def validate_remote_url(self, remote_url: str) -> None:
        if remote_url.startswith('git@'):
            return
        parsed = urlparse(remote_url)
        if parsed.scheme not in self.ALLOWED_SCHEMES:
            raise ValueError('Недопустимая схема remote URL')
        if parsed.hostname in self.BLOCKED_HOSTS:
            raise ValueError('Remote URL на локальный хост запрещен политикой')

    def validate_remote_name(self, name: str) -> None:
        if not name or any(ch.isspace() for ch in name):
            raise ValueError('Имя remote должно быть непустым и без пробелов')
