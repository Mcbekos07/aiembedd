# Agent core (текущее состояние)

## Назначение
Agent-слой управляет AI-задачами проекта: запуск task, запись шагов, патчи, память, checkpoint/rollback.

## Основные компоненты в коде
- API: `backend/app/api/routes/ai_tasks.py`, `ai_agent.py`, `ai_chat.py`, `ai_memory.py`
- Оркестрация: `backend/app/services/ai/ai_task_runner.py`
- Жизненный цикл задач: `backend/app/services/ai/ai_task_service.py`
- Циклы: `ai_compile_fix_loop_service.py`, `ai_runtime_observe_loop_service.py`
- Диагностика/патчи/память: `ai_diagnosis_service.py`, `ai_patch_service.py`, `ai_memory_service.py`

## Planner / Analyzer / Executor
- **Planner (явный отдельный модуль)**: отсутствует (**partial**).
- **Analyzer**: фактически реализован через `AIDiagnosisService` и log/context анализ.
- **Executor**: реализован через `AITaskRunner` + loop-сервисы + patch apply.

## Что уже реализовано
- Создание/статусы задач (`queued/running/succeeded/failed`).
- Лента действий задачи (`AITaskAction`) с payload.
- Pre-agent checkpoint + rollback option при неуспехе.
- Patch lifecycle: propose/apply/reject/rollback.
- Memory maintenance после циклов (promote/compact).

## TODO / partial
- Нет отдельного planner с явным plan graph/step scheduler.
- Нет полноценной очереди/асинхронного воркера (сейчас вызов task идёт в request flow).
- Guardrails/policies частично базовые (валидация действий есть, но без сложной policy engine).
