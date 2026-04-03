# AI module (backend)

## Назначение
Оркестрация AI-сценариев: chat/tasks/diagnosis/patch/memory и agent loops.

## Код
- API: `backend/app/api/routes/ai_chat.py`, `ai_tasks.py`, `ai_agent.py`, `ai_memory.py`, `ai_context_sources.py`
- Сервисы: `backend/app/services/ai/*`
- Модели: `backend/app/db/models/ai_*`
- WS: `backend/app/api/ws/ai_ws.py`

## Что делает
- Запуск и сопровождение AI задач.
- Подготовка и применение patch proposals.
- Memory уровни и provider routing.
- Compile-fix/runtime-observe loops (partial, зависит от runtime/toolchain).

## Связи
- `context`/`prompts` (входные данные для LLM)
- `build`/`logs` (диагностика и фиксы)
- `git` (checkpoint/rollback)
- frontend agent panel/task/diff/memory UI
