"""SemVer utilities."""


class SemverService:
    @staticmethod
    def bump(current: str, kind: str) -> str:
        major, minor, patch = (int(part) for part in current.split('.'))
        if kind == 'major':
            return f'{major + 1}.0.0'
        if kind == 'minor':
            return f'{major}.{minor + 1}.0'
        return f'{major}.{minor}.{patch + 1}'
