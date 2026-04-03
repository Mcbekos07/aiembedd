from fastapi import APIRouter

from app.services.devices.device_service import DeviceService

router = APIRouter(prefix='/devices', tags=['devices'])


@router.get('')
def list_devices() -> dict[str, object]:
    return {'status': 'ok', **DeviceService().list_devices()}
