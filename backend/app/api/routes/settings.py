"""Settings route definitions."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.db.models.system_setting import SystemSetting
from app.db.session import get_db_session

router = APIRouter(prefix='/settings', tags=['settings'])


class SettingsUpdateRequest(BaseModel):
    category: str
    value: str


@router.get('')
def get_runtime_settings(db: Session = Depends(get_db_session)) -> dict[str, object]:
    settings = get_settings()
    categories = ['theme', 'language', 'git', 'build', 'ai', 'security']
    data: dict[str, str] = {}
    for category in categories:
        row = db.query(SystemSetting).filter(SystemSetting.key == f'settings.{category}').first()
        data[category] = row.value if row else ''
    return {
        'status': 'ok',
        'label': 'Настройки',
        'debug': settings.debug,
        'database_url': settings.database_url,
        'categories': data,
    }


@router.post('')
def update_setting(payload: SettingsUpdateRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    key = f'settings.{payload.category}'
    row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not row:
        row = SystemSetting(key=key, value=payload.value)
        db.add(row)
    else:
        row.value = payload.value
    db.commit()
    return {'status': 'ok', 'message': 'Настройка обновлена'}
