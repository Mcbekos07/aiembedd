"""Custom domain exceptions."""


class AppError(Exception):
    """Base application exception."""


class ProjectNotFoundError(AppError):
    """Raised when requested project is not found."""
