# System Overview

## 1) Backend (FastAPI)
Основной вход: `backend/app/main.py`.

### Модули backend
- `app/api/routes/*`: REST-роуты (projects, files, builds, flash, logs, monitor, git, ai-* и др.).
- `app/api/ws/*`: WS-каналы (`/ws/ai`, `/ws/builds`, `/ws/logs`, `/ws/monitor`, `/ws/devices`).
- `app/services/*`: доменные сервисы (ai, context, build, git, files, monitor, logs, project, toolchains, versioning...).
- `app/db/*`: SQLAlchemy base/session/models.
- `app/config/*`: settings, paths, logging.

`app.lifecycle` создаёт runtime директории и таблицы БД при старте.

## 2) Frontend (Vue3 + Pinia)
Основной слой: `frontend/src/app`.

### Модули frontend
- `layouts/`, `pages/`, `components/*`: UI-структура IDE/AI/build/git/logs.
- `store/*`: состояние приложения (ai/build/project/git/realtime...).
- `services/*`: REST/WS клиенты к backend.
- `router.ts`: маршруты start/ide/build/ai/git/history/... .

## 3) Agent layer
- Backend: `app.services.ai.*`, маршруты `app/api/routes/ai_*`.
- Frontend: `components/ai/*`, `store/aiStore.ts`, `store/realtimeStore.ts`.
- Сценарии: запуск задач, шаги, патчи, подтверждение/применение.

## 4) Context engine
- Backend: `app.services.context.*` + `app.services.prompts.*`.
- Frontend: `ContextTransparencyPanel`, вызовы через `services/contextApi.ts`.
- Статус: **partial** (базовый pipeline и UI есть, глубина качества контекста зависит от runtime/backend данных).

## 5) Связи между слоями
1. Пользователь работает в IDE (ручное редактирование/build/flash/logs).
2. Frontend вызывает backend REST для операций и данных.
3. Realtime обновления приходят по WS и попадают в `realtimeStore`.
4. Agent/context/build панели синхронизируются через Pinia stores.

## TODO / partial
- Формальный versioned contract WS payload: **TODO**.
- Часть агентных сценариев зависит от реального toolchain/device/runtime: **partial**.
