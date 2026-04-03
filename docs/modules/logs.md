# Logs module (backend)

## Назначение
Получение и сжатое представление build/runtime логов для инженерной диагностики и AI-контекста.

## Код
- API: `backend/app/api/routes/logs.py`, `monitor.py`
- Сервисы: `backend/app/services/logs/*`, `backend/app/services/monitor/*`
- WS: `backend/app/api/ws/logs_ws.py`, `monitor_ws.py`

## Что делает
- Возврат raw logs и агрегатов (important/root cause/repeated warnings).
- Runtime monitor статус/логи.
- Выдача структурированных событий для UI и AI.

## Связи
- `build` (источник логов)
- `ai` (log context / diagnosis)
- frontend `logs_ui` и realtime store
