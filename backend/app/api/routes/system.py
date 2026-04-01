"""System route definitions."""

from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["system"])


@router.get("")
def get_system_overview() -> dict[str, str]:
    return {
        "status": "ok",
        "label": "Система",
        "message": "Базовый backend-каркас активен",
    }
