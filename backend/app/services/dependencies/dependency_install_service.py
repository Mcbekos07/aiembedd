"""Builds safe install plans without executing package managers."""

from app.services.dependencies.constants import SAFE_INSTALL_PACKAGES


class DependencyInstallService:
    def install_plan(self, packages: list[str]) -> dict[str, list[str]]:
        allowed = [pkg for pkg in packages if pkg in SAFE_INSTALL_PACKAGES]
        blocked = [pkg for pkg in packages if pkg not in SAFE_INSTALL_PACKAGES]
        return {'allowed': allowed, 'blocked': blocked}
