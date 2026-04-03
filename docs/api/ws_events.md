# WebSocket events (текущее состояние)

Все WS роуты имеют префикс `/ws`.

## Реально реализованные WS endpoints
| endpoint | первое сообщение от сервера | что дальше |
|---|---|---|
| `/ws/ai/{project_id}` | `{"type":"ai","project_id":...,"message":"AI канал подключен"}` | echo входящего текста: `{"type":"ai","payload":...}` |
| `/ws/builds/{project_id}` | `{"type":"status","project_id":...,"message":"Канал build статусов подключен"}` | echo: `{"type":"echo","payload":...}` |
| `/ws/logs/{project_id}` | `{"type":"log","project_id":...,"message":"Канал логов подключен"}` | echo: `{"type":"log","payload":...}` |
| `/ws/monitor/{project_id}` | `{"type":"monitor","project_id":...,"message":"Serial monitor канал подключен"}` | echo: `{"type":"monitor","payload":...}` |
| `/ws/devices` | `{"type":"devices","message":"Канал устройств подключен"}` | echo: `{"type":"devices","payload":...}` |

## События, которые frontend уже ожидает (но backend WS явно не эмитит как отдельные event-type)
- `agent_started`, `agent_step`, `task_finished`, `task_needs_confirmation`
- `build_started`, `build_failed`, `build_succeeded`
- `patch_ready`, `patch_applied`
- `flash_started`, `flash_result`
- `runtime_event`

Сейчас эти типы в основном формируются во frontend через нормализацию канала/локальные ingest события (**partial**).

## TODO
- Перейти от echo-каналов к доменным WS event payload (typed schema + version).
- Добавить подтверждения/heartbeat/reconnect protocol для production realtime.
