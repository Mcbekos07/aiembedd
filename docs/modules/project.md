# Project module (backend)

## Назначение
Управление проектами: создание, импорт, удаление, базовая мета-информация и project intelligence.

## Код
- API: `backend/app/api/routes/projects.py`
- Сервисы: `backend/app/services/project/*`
- Модели: `backend/app/db/models/project.py`, `project_remote.py`, `project_history.py`, `project_knowledge_snapshot.py`

## Что делает
- CRUD и импорт проекта.
- Возврат списка/деталей проекта для frontend.
- Вычисление/обновление project intelligence (partial).

## Связи
- `files` (дерево/контент файлов проекта)
- `git` (репозиторий внутри проекта)
- `build`/`logs` (история сборок по project_id)
- `ai`/`context` (контекст и задачи в рамках проекта)
