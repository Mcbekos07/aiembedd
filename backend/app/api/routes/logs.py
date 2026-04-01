from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models.build_job import BuildJob
from app.db.session import get_db_session

router = APIRouter(prefix='/logs', tags=['logs'])


@router.get('/build/{job_id}')
def get_build_logs(job_id: int, db: Session = Depends(get_db_session)) -> dict[str, str]:
    job = db.get(BuildJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Job не найден')
    try:
        with open(job.log_path, 'r', encoding='utf-8') as fp:
            raw = fp.read()
    except FileNotFoundError:
        raw = ''
    return {'status': 'ok', 'raw_log': raw, 'error_summary': job.error_summary}
