# Flash + runtime loop (текущее состояние)

## Как происходит прошивка
1. Frontend отправляет `POST /flash/{project_id}` с `programmer/port/confirmed`.
2. Backend подбирает programmer (`ProgrammerResolver`) и artifact (из build workspace или `artifact_path`).
3. `FlashService.flash(...)` валидирует подтверждение и совместимость port/programmer.
4. Через `FlasherRegistry` вызывается flasher; результат пишется в `FlashJob`.
5. При успехе фиксируется port binding, а результат добавляется в AI memory (`known_good_fix` / `flash_caveat`).

## Как читаются runtime логи
1. Запуск мониторинга: `POST /monitor/{project_id}/start`.
2. Проверка активной сессии: `GET /monitor/{project_id}/status`.
3. Чтение логов: `GET /monitor/sessions/{session_id}/logs`.
4. `SerialMonitorService.collect_runtime_log(...)` сейчас возвращает stub-лог (не реальный serial stream).
5. Лог прогоняется через `ImportantLogService` и `LogSummaryService`.

## TODO / partial
- Реальный serial backend для runtime stream: **TODO** (сейчас stub).
- Нет сложной автоматической реакции агента на runtime события в рамках отдельного flash-runtime state machine.
