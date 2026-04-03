# Context UI module (frontend)

## Назначение
Прозрачность контекста, который используется AI/агентом.

## Код
- Компонент: `frontend/src/app/components/ai/ContextTransparencyPanel.vue`
- API клиент: `frontend/src/app/services/contextApi.ts`
- Store: `frontend/src/app/store/aiStore.ts` (`loadContextTransparency`)

## Что делает
- Запрос context pack и показ источников (файлы/логи/размер/preview).
- Помогает объяснить «почему агент сделал действие».

## Связи
- backend `context`/`prompts`/`ai` сервисы
- `agent_panel` и `logs_ui`

## partial / TODO
- Глубокие метрики качества контекста в UI: **TODO**.
