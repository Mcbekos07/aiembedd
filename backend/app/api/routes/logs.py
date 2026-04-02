from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.models.build_job import BuildJob
from app.db.session import get_db_session
from app.services.logs.important_log_service import ImportantLogService
from app.services.logs.log_summary_service import LogSummaryService

router = APIRouter(prefix='/logs', tags=['logs'])


@router.get('/build/{job_id}')
def get_build_logs(job_id: int, last_n_critical: int = Query(12, ge=1, le=100), db: Session = Depends(get_db_session)) -> dict[str, object]:
    job = db.get(BuildJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Job не найден')
    try:
        with open(job.log_path, 'r', encoding='utf-8') as fp:
            raw = fp.read()
    except FileNotFoundError:
        raw = ''

    events = ImportantLogService().extract_events(raw)
    summary = LogSummaryService().summarize(events)
    ai_context = LogSummaryService().ai_ready_context(events, last_n_critical=last_n_critical)

    return {
        'status': 'ok',
        'raw_log': raw,
        'error_summary': job.error_summary,
        'important_summary': summary['important_summary'],
        'root_cause': summary['root_cause'],
        'repeated_warnings': summary['repeated_warnings'],
        'event_counts': summary['counts'],
        'ai_ready_context': ai_context,
        'critical_events': [e for e in events if str(e.get('severity')) == 'critical'][-last_n_critical:],
        'important_events': events,
    }
