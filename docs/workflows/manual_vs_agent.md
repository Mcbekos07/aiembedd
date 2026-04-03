# Manual vs Agent (текущее состояние)

## Что пользователь делает вручную
- В IDE: открыть/редактировать/сохранить файл.
- Запустить build/clean/rebuild/flash через build controls и quick actions.
- Смотреть raw/important логи и открывать файл по critical event.

## Где подключается AI
- Точечно: diagnose, chat, memory operations, patch review.
- Context transparency показывает, какие источники использованы для AI.

## Где работает агент
- Agent task flow через `ai-tasks` и `ai-agent`:
  - запуск задач;
  - task actions timeline;
  - patch lifecycle;
  - compile_fix_loop/runtime_observe_loop.
- В frontend это связано через `aiStore` + `realtimeStore` + AI панели.

## Текущее соотношение режимов
- Manual режим полностью доступен параллельно агенту (hybrid).
- Agent не заменяет ручной режим; это assist/orchestration слой.

## TODO / partial
- Часть агентного realtime/control UX зависит от backend WS payload и runtime-интеграций.
- Нет строгого state machine документа для переходов manual↔agent (сейчас поведение распределено по stores/services).
