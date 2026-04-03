"""Project template extension-point registry placeholder."""

from app.core.extension_points import PROJECT_TEMPLATE_KEYS


class ProjectTemplateService:
    def template_keys(self) -> tuple[str, ...]:
        return PROJECT_TEMPLATE_KEYS
