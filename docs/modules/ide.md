# IDE module (frontend)

## Назначение
Инженерная оболочка IDE: файл-дерево, редактор, быстрые ручные действия, связка с AI/build/logs.

## Код
- Страница: `frontend/src/app/pages/IdePage.vue`
- Компоненты: `frontend/src/app/components/ide/*`
- Связанные stores: `projectStore.ts`, `buildStore.ts`, `aiStore.ts`, `realtimeStore.ts`

## Что делает
- Manual editing (open/save file).
- Быстрые действия: build/flash/AI explain/fix.
- Компоновка гибридного UX (manual + agent).

## Связи
- `agent_panel`, `logs_ui`, `context_ui`
- backend `project/files/build/logs/ai` API
