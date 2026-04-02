# Agent Checkpoints

## Types
- pre_agent_checkpoint
- pre_patch_checkpoint
- manual
- successful-fix snapshots (via version note/task linkage)

## API
- `GET /git/{project_id}/checkpoints`
- `POST /git/{project_id}/checkpoints`
- `POST /git/{project_id}/checkpoints/restore`
- `POST /git/{project_id}/suggest-commit-message`
- `POST /git/{project_id}/version-from-task`

## Rollback
Restore uses git hard reset to checkpoint commit hash. Use only with explicit user intent.

## Linkage
Checkpoint rows store `task_id`, and versions store fix notes, so UI can trace task ↔ git action ↔ version snapshot.
