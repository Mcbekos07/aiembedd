# Agent panel module (frontend)

## Назначение
UI-контур наблюдения и управления агентом внутри IDE (не отдельный продукт).

## Код
- Компоненты: `frontend/src/app/components/ai/AgentPanel.vue`, `AiTaskPanel.vue`, `AiTaskHistory.vue`, `AiDiffPreview.vue`
- Store: `frontend/src/app/store/aiStore.ts`
- Realtime: `frontend/src/app/store/realtimeStore.ts`

## Что делает
- Показ статуса задачи/шага/подтверждения.
- Stop/clear/retry и patch review/apply/reject/rollback.
- Синхронизация статусов через polling + WS events.

## Связи
- backend `ai` API и `/ws/ai`
- `ide` (общий workflow пользователя)
- `logs_ui`/`context_ui` для объяснимости действий
