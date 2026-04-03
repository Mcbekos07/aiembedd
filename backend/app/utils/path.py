"""Path utility helpers."""

from pathlib import Path


def resolve_project_path(path: str) -> Path:
    """Resolve and normalize project path to absolute path."""
    return Path(path).expanduser().resolve()


def safe_child_path(base_path: str, rel_path: str) -> Path:
    """Resolve child path and ensure it stays inside the base directory."""
    base = resolve_project_path(base_path)
    target = (base / rel_path).resolve()
    if base not in target.parents and base != target:
        raise ValueError('Path outside project root')
    return target
