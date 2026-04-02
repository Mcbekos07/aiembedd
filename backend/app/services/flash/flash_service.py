from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models.flash_job import FlashJob
from app.db.models.project import Project
from app.services.ai.ai_memory_service import AIMemoryService
from app.services.toolchains.flasher_registry import FlasherRegistry


class FlashService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def flash(
        self,
        project: Project,
        programmer: str,
        port: str,
        artifact_path: str,
        *,
        confirmed: bool,
        allow_mismatch: bool = False,
    ) -> FlashJob:
        if not confirmed:
            raise ValueError('Flash requires explicit confirmation')

        if project.default_port and project.default_port != port and not allow_mismatch:
            raise ValueError('Port mismatch with project binding; set allow_mismatch=true to override')
        if project.default_programmer and project.default_programmer != programmer and not allow_mismatch:
            raise ValueError('Programmer mismatch with project binding; set allow_mismatch=true to override')

        path = Path(artifact_path)
        if not path.exists() or path.suffix.lower() not in {'.bin', '.hex', '.elf', '.uf2'}:
            raise ValueError('Artifact missing or unsupported format (.bin/.hex/.elf/.uf2 required)')

        job = FlashJob(project_id=project.id, status='queued', programmer=programmer, port=port)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        flasher = FlasherRegistry().get(programmer)
        if not flasher:
            job.status = 'failed'
            job.output = f'Unknown programmer: {programmer}'
            self.db.commit()
            AIMemoryService(self.db).add_typed(project.id, 'flash_caveat', 'unknown_programmer', job.output, importance=4, source='flash')
            return job

        try:
            output = flasher.flash(str(path), port)
            job.status = 'success'
            job.output = output
        except Exception as exc:
            job.status = 'failed'
            job.output = f'Flash error: {exc}'
        self.db.commit()
        mem_type = 'known_good_fix' if job.status == 'success' else 'flash_caveat'
        AIMemoryService(self.db).add_typed(project.id, mem_type, f'flash_{job.status}', job.output[:300], importance=4 if job.status == 'failed' else 3, source='flash')
        return job
