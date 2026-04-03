"""Safe patch lifecycle service with checkpoint/apply/reject/rollback flows."""

from __future__ import annotations

import difflib

from sqlalchemy.orm import Session

from app.db.models.ai_patch_set import AIPatchSet
from app.db.models.project import Project
from app.schemas.ai_patch import PatchProposalRequest
from app.services.ai.ai_memory_service import AIMemoryService
from app.services.context.context_pipeline_service import ContextPipelineService
from app.services.files.file_service import FileService
from app.services.git.git_checkpoint_service import GitCheckpointService
from app.services.git.git_service import GitService
from app.services.history.event_write_service import EventWriteService


class AIPatchService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def propose(self, payload: PatchProposalRequest) -> AIPatchSet:
        project = self.db.get(Project, payload.project_id)
        if not project:
            raise ValueError('Проект не найден')
        if not payload.changes:
            raise ValueError('Patch set не содержит изменений')


        try:
            pipeline = ContextPipelineService(self.db).build(project, task_text=payload.reason or payload.summary, mode='refactor_task')
            EventWriteService(self.db).write(project.id, 'context_pipeline_patch_proposal', 'Context pipeline assembled for patch proposal', str(pipeline['report'])[:1200])
        except Exception:
            pass

        file_service = FileService()
        checkpoint: dict[str, str] = {}
        diff_chunks: list[str] = []

        for change in payload.changes:
            old_content = ''
            try:
                old_content = file_service.read(project.path, change.path)
            except Exception:
                old_content = ''
            checkpoint[change.path] = old_content

            diff = difflib.unified_diff(
                old_content.splitlines(),
                change.new_content.splitlines(),
                fromfile=f'a/{change.path}',
                tofile=f'b/{change.path}',
                lineterm='',
            )
            diff_chunks.append('\n'.join(diff))

        patch = AIPatchSet(
            project_id=project.id,
            reason=payload.reason,
            summary=payload.summary,
            dangerous='yes' if payload.dangerous else 'no',
            changes=[c.model_dump() for c in payload.changes],
            checkpoint=checkpoint,
            diff_preview='\n\n'.join(diff_chunks),
            status='pending',
        )
        self.db.add(patch)
        self.db.commit()
        self.db.refresh(patch)

        EventWriteService(self.db).write(project.id, 'ai_patch_proposed', 'AI patch proposal created', payload.reason)
        for change in payload.changes:
            AIMemoryService(self.db).add_typed(
                project.id,
                'known_risky_file',
                change.path[:80],
                f'Patch touched file during proposal: {payload.reason}',
                importance=3,
                source='patch_proposal',
            )
        return patch

    def apply(self, patch_id: int, confirmed: bool) -> AIPatchSet:
        patch = self._get_patch(patch_id)
        if patch.status != 'pending':
            raise ValueError('Patch уже обработан')
        if patch.dangerous == 'yes' and not confirmed:
            raise ValueError('Опасный patch требует подтверждения')

        project = self.db.get(Project, patch.project_id)
        if not project:
            raise ValueError('Проект не найден')

        try:
            GitCheckpointService(self.db).create_checkpoint(project, 'pre_patch_checkpoint', patch.summary or patch.reason, task_id=0, note=f'patch_id={patch.id}')
        except Exception:
            pass

        file_service = FileService()
        for item in patch.changes:
            file_service.save(project.path, item['path'], item['new_content'])

        git_status = ''
        try:
            git_status = GitService().run(project.path, ['status', '--short'])
        except Exception:
            git_status = 'git status unavailable'

        patch.status = 'applied'
        patch.git_status_after_apply = git_status
        self.db.commit()

        EventWriteService(self.db).write(project.id, 'ai_patch_applied', 'AI patch applied', patch.summary or patch.reason)
        AIMemoryService(self.db).add_typed(
            project.id,
            'known_good_fix',
            (patch.summary or patch.reason)[:80] or 'applied_patch',
            f"Applied patch id={patch.id}; files={[item['path'] for item in patch.changes]}",
            importance=4,
            source='patch_apply',
        )
        return patch

    def reject(self, patch_id: int) -> AIPatchSet:
        patch = self._get_patch(patch_id)
        if patch.status != 'pending':
            raise ValueError('Можно отклонять только pending patch')
        patch.status = 'rejected'
        self.db.commit()

        EventWriteService(self.db).write(patch.project_id, 'ai_patch_rejected', 'AI patch rejected', patch.reason)
        return patch

    def rollback(self, patch_id: int) -> AIPatchSet:
        patch = self._get_patch(patch_id)
        if patch.status != 'applied':
            raise ValueError('Rollback доступен только для applied patch')

        project = self.db.get(Project, patch.project_id)
        if not project:
            raise ValueError('Проект не найден')

        file_service = FileService()
        for path, content in patch.checkpoint.items():
            file_service.save(project.path, path, content)

        patch.status = 'rolled_back'
        self.db.commit()

        EventWriteService(self.db).write(project.id, 'ai_patch_rolled_back', 'AI patch rolled back', patch.reason)
        return patch

    def list_by_project(self, project_id: int) -> list[AIPatchSet]:
        return list(
            self.db.query(AIPatchSet)
            .filter(AIPatchSet.project_id == project_id)
            .order_by(AIPatchSet.created_at.desc())
            .all()
        )

    def _get_patch(self, patch_id: int) -> AIPatchSet:
        patch = self.db.get(AIPatchSet, patch_id)
        if not patch:
            raise ValueError('Patch не найден')
        return patch
