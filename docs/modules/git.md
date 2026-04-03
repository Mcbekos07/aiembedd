# Git module (backend)

## Назначение
Операции с git-репозиторием проекта: статус, ветки, коммиты, diff, remote, checkpoints/restore.

## Код
- API: `backend/app/api/routes/git.py`, `branches.py`, `remote_git.py`, `versions.py`
- Сервисы: `backend/app/services/git/*`, `backend/app/services/versioning/*`
- Модели: `backend/app/db/models/git_branch.py`, `git_commit.py`, `version.py`

## Что делает
- Базовые git-операции и remote-политики.
- Checkpoint/restore сценарии.
- Версионирование и история версий (partial).

## Связи
- `project` (репозиторий в контексте проекта)
- `ai` (патчи/откаты через checkpoints)
- frontend IDE/diff/versions панели
