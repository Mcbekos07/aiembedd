from fastapi import APIRouter

from app.services.toolchains.detection_service import ToolchainDetectionService
from app.services.toolchains.registry import ToolchainRegistry

router = APIRouter(prefix='/toolchains', tags=['toolchains'])


@router.get('')
def list_toolchains() -> dict[str, object]:
    return {'status': 'ok', 'items': ToolchainRegistry().list_names()}


@router.get('/detect')
def detect_toolchains() -> dict[str, object]:
    return {'status': 'ok', 'items': ToolchainDetectionService().detect()}
