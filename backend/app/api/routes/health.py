"""Health route definitions."""

from fastapi import APIRouter

from app.services.system.health_service import HealthService

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health() -> dict[str, str]:
    return HealthService.get_health()
