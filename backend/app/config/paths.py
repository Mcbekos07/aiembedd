"""Filesystem paths used by backend services."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
WORKSPACES_DIR = DATA_DIR / "workspaces"
RUNNERS_DIR = DATA_DIR / "runners"
CONFIGS_DIR = ROOT_DIR / "configs"


def ensure_runtime_dirs() -> None:
    """Ensure required runtime directories exist."""
    for path in (DATA_DIR, WORKSPACES_DIR, RUNNERS_DIR, CONFIGS_DIR):
        path.mkdir(parents=True, exist_ok=True)
