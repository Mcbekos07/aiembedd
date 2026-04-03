# Logs UI module (frontend)

## Назначение
Отображение raw build/runtime логов и инженерных сводок для диагностики.

## Код
- Компоненты: `frontend/src/app/components/logs/*`
- Build страница: `frontend/src/app/pages/BuildPage.vue`
- Store: `frontend/src/app/store/buildStore.ts`

## Что делает
- Показ raw logs (без перевода).
- Показ summary/root cause/critical events.
- Переход к файлу по событию (через project store).

## Связи
- backend `logs`/`monitor`/`build` API + WS каналы
- `ide`/`agent_panel` (совместный цикл diagnose/fix)
