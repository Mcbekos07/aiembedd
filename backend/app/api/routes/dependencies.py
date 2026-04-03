from fastapi import APIRouter
from pydantic import BaseModel

from app.services.dependencies.dependency_check_service import DependencyCheckService
from app.services.dependencies.dependency_install_service import DependencyInstallService

router = APIRouter(prefix='/dependencies', tags=['dependencies'])


class InstallRequest(BaseModel):
    packages: list[str]


@router.get('/check')
def check_dependencies() -> dict[str, object]:
    return {'status': 'ok', 'items': DependencyCheckService().check()}


@router.post('/install-plan')
def install_plan(payload: InstallRequest) -> dict[str, object]:
    return {'status': 'ok', **DependencyInstallService().install_plan(payload.packages)}
