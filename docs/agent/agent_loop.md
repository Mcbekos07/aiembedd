# Agent loop (текущее поведение)

## Поток обработки задачи
1. `POST /ai-tasks/{project_id}` вызывает `AITaskRunner.run(...)`.
2. Создаётся запись `AITask` со статусом `queued`.
3. Для loop-задач (`compile_fix_loop`, `runtime_observe_loop`) создаётся pre-agent checkpoint.
4. Выполняется соответствующий loop-service, шаги пишутся в `AITaskAction`.
5. При успехе: `succeeded`, может создаваться version snapshot.
6. При ошибке/остановке: `failed`, может добавляться rollback option.

## Для compile-fix loop
- На итерации запускается build.
- Если build успешен: loop завершается.
- Если build failed: запускается diagnosis.
- При safe_auto_fix_possible: пробуется patch propose+apply.
- Иначе loop останавливается с причиной.

## Что уже реализовано
- Ограничение числа итераций в loop.
- Причины остановки (`build_succeeded`, `unsafe_auto_fix`, `no_safe_patch`, `max_iterations_reached`).
- Запись событий в history и typed memory.

## TODO / partial
- Нет внешнего planner-а для динамической перестройки стратегии между итерациями.
- Нет распределённого execution/queue orchestration.
- Realtime-ack/control channel на backend минимальный (WS есть, но без сложного протокола подтверждений).
