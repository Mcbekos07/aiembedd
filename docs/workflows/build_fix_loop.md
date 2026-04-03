# Build fix loop (текущее состояние)

## Как сейчас работает сборка
1. Frontend вызывает backend build endpoints (`/builds/{project_id}/prepare|run|clean|rebuild`).
2. `BuildService.start(...)` создаёт workspace, запускает команду toolchain и пишет `BuildJob`.
3. По завершению job получает `success/failed`, а `error_summary` формируется через `BuildSummaryService`.

## Как обрабатываются ошибки
- Ошибки сборки отражаются в `BuildJob.status=failed` и `error_summary`.
- Логи и важные события доступны через `logs`/`monitor` API и UI панели логов.
- В frontend `buildStore` держит `rootCause`, `importantSummary`, `criticalEvents`.

## Есть ли автоматизация
- Есть agent-сценарий `compile_fix_loop` в `AICompileFixLoopService`:
  - итерационный build;
  - diagnosis при fail;
  - попытка safe patch propose+apply;
  - остановка по причинам (`unsafe_auto_fix`, `no_safe_patch`, `max_iterations_reached`).
- Автоматизация ограниченная и эвристическая (**partial**).

## TODO / partial
- Нет отдельного асинхронного orchestration/queue для loop задач.
- Нет продвинутой стратегии выбора фиксов (planner/reranker) между итерациями.
