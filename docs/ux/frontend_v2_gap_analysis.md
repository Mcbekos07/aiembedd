# Frontend V2 Gap Analysis (Этап 1: аудит текущего фронтенда)

## 1) Цель Frontend V2

Frontend V2 должен эволюционно развить текущий UI в **гибридную инженерную среду**:
- IDE shell для ручной инженерной работы.
- Встроенное агентное управление и AI-assist.
- Прозрачность агентных действий (что/почему/на каких данных).
- Dual-mode UX: ручной режим и агентный режим одновременно, без взаимного исключения.

Ключевой принцип: **не заменять ручной режим агентом**, а интегрировать агента в IDE workflow.

---

## 2) Текущее состояние (as-is)

### 2.1 Layouts и роутинг

Что уже есть:
- Базовая layout-структура (`MainLayout`, `StartLayout`, `IdeLayout`) с маршрутизацией через `vue-router`.
- Отдельные страницы по доменам: IDE, Build, Git, History, AI, Environment, Devices, Prompts, Settings.

Ограничения:
- Навигация в шапке уже функциональна, но домены разнесены на разные страницы, а **сквозной “IDE + Agent + Timeline + Logs” рабочий контур слабый**.
- Нет route-level сценариев для полуавтоматических агентных сессий (например, единая рабочая “операция” с прогрессом по этапам).

### 2.2 IDE и ручной режим

Что уже есть:
- `IdePage` содержит файловую навигацию (`FileTree`), редактор (`CodeEditor`), quick actions, git/build/ai блоки.
- `projectStore` поддерживает ручной цикл: открыть файл, редактировать, сохранить.

Ограничения:
- Редактор пока textarea-fallback (без инженерных функций уровня Monaco).
- `QuickActions` визуально есть, но часть кнопок не связана с реальным flow.
- Нет стабильной визуализации “manual + AI coexistence” прямо в редакторном контексте (например, inline AI suggestions на текущий файл/диапазон).

### 2.3 AI/Agent UX

Что уже есть:
- `AiPage` агрегирует chat/diagnosis/tasks/memory/patch diff.
- Есть actions для patch proposal/apply/reject/rollback.
- Есть task history с action timeline.

Ограничения:
- Агентный UX в основном концентрирован в отдельной странице, а не встроен в IDE shell как first-class workflow.
- Слабая explainability на уровне UI:
  - нет явной панели “почему выбран этот файл/лог/контекст”; 
  - нет визуального breakdown контекстного бюджета/приоритетов;
  - нет удобной связки task action -> изменение в конкретном файле в редакторе.
- Часть пользовательских текстов смешана (RU/EN), что противоречит требованию русскоязычного UI.

### 2.4 Build / Logs / Runtime

Что уже есть:
- `BuildPage` объединяет build controls, history, runtime status, log summary и raw log.
- `buildStore` хранит важные события/корневую причину/critical events/runtime summary.
- Логи отображаются в оригинале (важно и соответствует требованию).

Ограничения:
- Нет realtime-канала в UI (polling/refresh есть частично, но единая live-модель не доведена).
- Нет сквозной связи “агент увидел важный лог -> объяснил -> предложил правку -> diff -> apply” в одном рабочем месте.
- Недостаточно визуальных индикаторов состояния “agent is thinking/collecting logs/proposing patch”.

### 2.5 Git / History / Versioning

Что уже есть:
- Базовые панели Git (ветки, diff, commit, remotes).
- Чекпоинты агента и операции восстановления.
- История проекта и версияция.

Ограничения:
- Нет общей timeline-корреляции: build события, AI task actions, git checkpoints, patch lifecycle в единой оси времени.
- Слабая “diff approval workflow” визуально (нет явного статуса проверки человеком перед применением в IDE-контексте).

### 2.6 Stores и сервисы

Что уже есть:
- Разделение по доменным Pinia stores (`project`, `build`, `ai`, `git`, `history`, `device`, `prompt`).
- Централизованный API client, структурированные сервисы для REST API.

Ограничения:
- Stores mostly independent; нет “session orchestration store” для hybrid workflow (manual+agent).
- Нет frontend-обвязки WebSocket событий для realtime agent/build/log статуса.
- Нет нормализованной модели UI-state для explainability report (selected files/logs/context reason chain).

---

## 3) Reusable pieces для Frontend V2 (что уже подходит)

Ниже — компоненты/слои, которые можно **эволюционно расширять**, а не переписывать:

1. **Структура роутов и layouts**: можно сохранить текущую и добавить V2-потоки поверх.
2. **`IdePage` каркас**: уже есть основа IDE-shell с sidebar/editor/right panels/logs.
3. **`projectStore` + `fileApi`**: ручной file workflow уже работает.
4. **`buildStore` + build/log панели**: хорошая база для инженерного observability UX.
5. **`aiStore` + agent компоненты**: есть заготовка для task/patch/memory lifecycle.
6. **`gitStore` + checkpoint/version панели**: основа для human approval и rollback safety.
7. **`apiClient` + сервисный слой**: единая точка интеграции с backend REST.

Вывод: архитектура фронтенда уже модульная и подходит для incremental V2.

---

## 4) Критичные UX gaps для Frontend V2

### Gap A — Недостаточный dual-mode UX
- Ручной и агентный режим существуют рядом, но не формируют единый сценарий.
- Нужно сделать “agent assist in context”, а не “AI отдельно на другой странице”.

### Gap B — Слабая прозрачность действий агента
- Нет явной панели с ответами на вопросы:
  - что агент делает сейчас,
  - почему выбрал эти файлы,
  - какие логи использует,
  - какой контекст собран,
  - на каком шаге пайплайна находится.

### Gap C — Недостаточная realtime-интеграция
- Для agent/build/log pipeline не хватает live-состояния (WebSocket event ingestion, unified status badges, timeline updates).

### Gap D — Diff approval / rollback как инженерный workflow не выражен
- Есть отдельные кнопки apply/reject/rollback, но нет UX-потока “предложение -> ревью -> подтверждение -> применение -> пост-статус”.

### Gap E — Разнородность UI-копирайта
- Интерфейс частично на русском, частично на английском.
- Для V2 нужен единый RU UI-тон (кроме оригинальных build/compiler/runtime логов).

### Gap F — Разорванная timeline-модель
- Build, AI task actions, git checkpoints, project history не сведены в единый инженерный timeline.

---

## 5) Required event/state integration для V2

Минимально необходимая интеграция:

1. **Unified Agent Session State (frontend)**
   - состояния: idle / collecting_context / diagnosing / proposing_patch / waiting_approval / applying / done / failed.
   - источник: REST + WebSocket events.

2. **Realtime streams**
   - runtime/build logs,
   - agent task progress,
   - patch lifecycle transitions.

3. **Context transparency model**
   - selected_files (+ reasons/relevance),
   - selected_logs,
   - memory usage summary,
   - token budget usage / dropped fragments reason.

4. **Human approval state machine**
   - draft proposal -> reviewed -> approved/rejected -> applied/rolled-back.

5. **Cross-module synchronization**
   - при выборе critical log/event — быстрый переход к файлу/редактору,
   - при применении patch — обновление git diff/status/editor views.

---

## 6) Recommended implementation order (эволюционный план)

### Шаг 1 (текущий этап, завершён): аудит + gap map
- Зафиксировать текущее состояние и список пробелов.

### Шаг 2: UX-консолидация в IDE shell (без ломки роутов)
- Усилить `IdePage` как основную рабочую поверхность: manual editing + AI assist + logs + diff review.
- Сохранить отдельные страницы (AI/Build/Git) как детальные режимы.

### Шаг 3: Agent transparency panels
- Добавить панели статуса агента и explainability (selected files/logs/reasons).
- Подтянуть context report из backend в UI.

### Шаг 4: Realtime event integration
- Ввести websocket/event layer и индикаторы live-статуса.
- Привязать realtime updates к timeline и ключевым панелям.

### Шаг 5: Diff approval workflow hardening
- Улучшить UX-цепочку review/approve/reject/rollback с понятными статусами и последствиями.

### Шаг 6: Русификация UI и UX polishing
- Привести все пользовательские тексты к единому русскому стилю.
- Сохранить оригинал логов без изменения контента.

---

## 7) Риски и guardrails

1. Не создавать параллельную архитектуру: расширять существующие pages/components/stores.
2. Не ломать существующие роуты и базовые manual flows.
3. Любые V2-добавления проверять на сценариях:
   - открыть файл -> ручная правка -> build/flash -> анализ логов,
   - AI explain/fix -> diff review -> apply/rollback,
   - ручной и агентный режимы в одной сессии.

---

## 8) Итог этапа 1

Текущий фронтенд уже содержит пригодный каркас для Frontend V2 (IDE, AI, Build, Git, History, stores/services), но требует:
- сквозной dual-mode orchestration,
- прозрачности агентных решений,
- realtime state/event visualization,
- усиленного инженерного diff/timeline UX,
- полного RU UI-копирайта.

Эволюционный путь реалистичен: критическая база уже реализована и переиспользуема.
