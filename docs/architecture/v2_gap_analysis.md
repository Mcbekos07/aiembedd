# V2 Gap Analysis (Audit only)

## Scope and constraints

- Аудит выполнен на существующей кодовой базе без rearchitecture и без добавления нового продуктового функционала.
- Цель: оценить готовность текущей платформы к V2 (embedded agent platform / AntiGravity for MCU) и зафиксировать точечные пробелы.

## 1) Текущее состояние по доменам

### 1.1 Projects
- Есть рабочий CRUD-слой реестра проектов (`ProjectService`, routes `/projects`).
- Есть режимы удаления (`registry_only`, `registry_with_history`, `full`) через `ProjectDeleteService`.
- Для V2 это годная база project registry/state.

### 1.2 Files / Editor
- Есть безопасные файловые операции в `FileService` (path traversal guard + запрет удаления project root).
- Есть API для tree/read/save/rename/delete/create.
- Frontend store уже работает с file tree/open/save.
- Для V2 подходит как минимальный filesystem layer, но без collaborative editing, locks и дифф-операций.

### 1.3 Git / Version / History
- Есть safe git wrapper с allowlist подкоманд (`GitService.ALLOWED`).
- Есть remote policy hooks для URL/name.
- Есть semver bump + version entity + history event write.
- Для V2 годно как базовая обвязка, но без полноценного graph-aware workflow (PR-like review, merge policies, branch protections).

### 1.4 Builds
- Есть job-модель и `BuildService` с workspace/log path/error summary.
- Есть command guard allowlist в `BuildExecutorService`.
- Есть маршруты prepare/run/clean/rebuild/history/stop.
- Текущая реализация синхронная и skeleton-уровня для реального agent-loop orchestration.

### 1.5 Flash / Devices
- Есть `FlashService`, `ProgrammerResolver`, `DeviceService` и extension points.
- Текущий flash flow mock-like (быстрое queued -> success, без реальной очереди/retry/hardware feedback loop).
- Device discovery частично mock/integration stub.

### 1.6 Logs
- Есть базовые маршруты и сервисы summary/important logs.
- Лог-слой пока utility-уровня, без единой корреляции run/build/flash/agent task timeline.

### 1.7 AI / Prompt / Memory / Tasks
- Есть `AIChatService`, `AITaskService`, `AITaskRunner`, `AIMemoryService`, prompt versioning.
- Есть policy-каркас (`ActionPolicy`) и provider registry.
- Но agent cycle пока не завершён как stateful orchestrator (план -> действия -> проверки -> rollback/confirm).

### 1.8 Frontend
- Есть router/layout/pages/store/api service split.
- `projectStore` содержит прямой `fetch` в `deleteProject` (обходит `apiClient`) — локальная дубликация transport слоя.
- Страницы компонуются, но часть agent/build/flash экранов завязана на skeleton backend ответы.

## 2) Что уже пригодно для V2 без изменений

1. Project registry + базовые project routes.
2. Безопасный файловый слой (safe child path + root delete guard).
3. Git wrapper с allowlist и remote policy hook.
4. Базовый semver/version/history контур.
5. Extension-point реестры (toolchains/flashers/providers/scanners/templates) как каркас расширяемости.
6. Frontend routing/layout/store separation как основа UI-потоков.

## 3) Что является skeleton и требует доработки

1. **Agent cycle orchestration**
   - Сейчас AI-task runner фактически делает chat-call и помечает task done.
   - Нет многошагового execution graph, checkpoints, approval gates, retry policy.

2. **Build/Flash execution model**
   - Синхронные операции в HTTP request scope.
   - Нет фоновой очереди/воркеров и telemetry hooks для agent feedback.

3. **Device/flash reliability layer**
   - Нет устойчивой модели сессий устройства, reattach, health heartbeat.
   - Flash workflow близок к stub.

4. **Logs observability**
   - Нет единой нормализованной run timeline (task/build/flash/git/action).
   - Нет качественной корреляции событий для аудита agent decisions.

5. **Frontend data-flow consistency**
   - Точечные обходы api client/store abstraction (пример deleteProject в store).

## 4) Дубли / слабые места / неиспользуемые или слишком общие абстракции

### Дубли / несогласованности
- В frontend store есть прямой `fetch` вместо использования `projectApi/apiClient` (локальная дубликация transport ответственности).
- Есть пересечение терминов task/chat/action между несколькими AI сервисами без единой orchestration модели.

### Слабые места
- Build/flash/log flows в основном synchronous + minimal status model.
- Недостаточная явная модель agent action lifecycle (intent -> policy -> execute -> verify -> persist trace).

### Неиспользуемые/слишком общие места
- Ряд adapter/provider/flasher классов являются extension stubs с минимальной логикой (полезно как каркас, но не production behavior).

## 5) Пробелы до V2 (missing capabilities)

1. Stateful agent runtime (goal decomposition, planning, action queue, tool-calling loop).
2. Human-in-the-loop safety workflow (review/apply/rollback with persisted checkpoints).
3. Background execution infrastructure for long-running build/flash/actions.
4. Device-aware execution policy (board profile, port stability, reconnect strategy).
5. Unified observability/audit model for agent traceability.
6. Consistent frontend UX around agent lifecycle states (planned/running/waiting-confirmation/failed/rolled-back).

## 6) Рекомендуемая последовательность доработок (V2 phases)

### Phase 2 — Agent Runtime Core
- Ввести state machine для agent tasks.
- Сохранение шагов/решений/артефактов в DB (без ломки существующих routes).
- Вынести orchestration из route-level handlers в dedicated service layer.

### Phase 3 — Async Execution Backbone
- Ввести фоновые worker-процессы для build/flash/long tasks.
- Привязать logs/history/events к execution-id.
- Добавить retry/cancel/timeout policy.

### Phase 4 — Embedded Reliability Layer
- Device session manager + port binding stability.
- Реальные flasher adapters + error taxonomy.
- Policy-driven safe actions per platform/toolchain.

### Phase 5 — Frontend Agent UX
- Единый экран agent run timeline.
- Явные статусы шагов и confirmation points.
- Убрать transport дубли, закрепить единый API access pattern.

## 7) Минимальные служебные улучшения, допустимые на этапе аудита

- Добавлять только docstrings/comments в критичных местах, если это повышает читаемость.
- Избегать структурных миграций до старта следующего этапа.
