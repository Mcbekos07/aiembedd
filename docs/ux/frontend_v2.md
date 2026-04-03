# Frontend V2 (финальный polish)

## Цель
Frontend V2 развивает существующую архитектуру без переписывания: IDE shell + manual workflow + AI assist + agent-driven режим в едином инженерном UX.

## Что проверено на этапе polish
- Согласованность слоёв `layouts / router / pages / stores / services / realtime`.
- Сосуществование ручного и агентного контуров в `IdePage` и `BuildPage`.
- Наличие понятных состояний: loading / empty / error для ключевых AI/build/log/diff панелей.
- Русификация пользовательских UI-текстов (raw build/runtime logs оставлены в оригинале).

## Ключевые UX-правила
1. Пользователь всегда может вручную открыть/править файл и запустить build/flash.
2. AI-помощь вызывается точечно и не блокирует ручной сценарий.
3. Агентные действия, патчи и risky-flow визуально прозрачны.
4. Realtime события учитываются как для IDE, так и для build/runtime экрана.

## Ключевые точки расширения
- `frontend/src/app/pages/IdePage.vue`
- `frontend/src/app/components/ai/AgentPanel.vue`
- `frontend/src/app/components/ai/AiDiffPreview.vue`
- `frontend/src/app/components/ide/QuickActions.vue`
- `frontend/src/app/store/aiStore.ts`
- `frontend/src/app/store/buildStore.ts`
- `frontend/src/app/store/realtimeStore.ts`
