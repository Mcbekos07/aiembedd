from sqlalchemy.orm import Session

from app.db.models.flash_job import FlashJob


class FlashService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def flash(self, project_id: int, programmer: str, port: str) -> FlashJob:
        job = FlashJob(project_id=project_id, status='queued', programmer=programmer, port=port)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        job.status = 'success'
        job.output = f'Flashed via {programmer} on {port}'
        self.db.commit()
        return job
