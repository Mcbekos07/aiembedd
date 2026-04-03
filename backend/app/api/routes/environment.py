from fastapi import APIRouter

from app.config.paths import CONFIGS_DIR, DATA_DIR, RUNNERS_DIR, WORKSPACES_DIR

router = APIRouter(prefix='/environment', tags=['environment'])


@router.get('')
def get_environment() -> dict[str, object]:
    return {
        'status': 'ok',
        'label': 'Окружение',
        'paths': {
            'data': str(DATA_DIR),
            'workspaces': str(WORKSPACES_DIR),
            'runners': str(RUNNERS_DIR),
            'configs': str(CONFIGS_DIR),
        },
    }
