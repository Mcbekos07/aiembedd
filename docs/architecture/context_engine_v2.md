# Context Engine V2 — Audit & Design Map

## 1) Текущее состояние (аудит существующей базы)

### 1.1 Что уже есть и может быть базой

- **Context entrypoint**: `AIContextService` делегирует сборку в `ContextAssembler` для общего и diagnosis-контекста.
- **Context assembly**: `ContextAssembler` уже тянет memory, diff, build summary, important logs, project intelligence, selected file.
- **Budget guard**: `ContextBudgetService.trim(...)` ограничивает размер итогового текста.
- **Memory V2**: `AIMemoryService` хранит typed memory, умеет query/summarize/compact/promote history.
- **History source**: `HistoryService.list_events(...)` дает project-scoped timeline.
- **Git source**: `GitService` + `GitDiffService` + checkpoints (`GitCheckpointService`) для долговременной инженерной памяти и состояния изменений.
- **Build/runtime logs**: `ImportantLogService` + `LogSummaryService` + `SerialMonitorService.collect_runtime_log(...)`.
- **Project structure source**: `ProjectIntelligenceService` (important/risky files, dependency map, known build paths, entry points).

### 1.2 Где уже есть context assembly, но пока слишком простой

- `ContextAssembler.assemble(...)` и `assemble_diagnosis(...)` — сейчас это в основном **конкатенация источников** с легким slicing, без retrieval-score/ranking по релевантности задачи.
- `ContextBudgetService` оперирует `max_chars`, но нет токен-ориентированного budgeting по слоям (active/warm/cold).
- Нет явного разделения payload на **active context / warm memory / cold memory references**.

---

## 2) Обнаруженные пробелы

1. **Ranking/Retrieval gap**
   - Нет единого scorer'а релевантности для memory/history/git/log/file chunks.
   - Нет query-aware отбора по intent (debug build vs runtime vs versioning vs patch review).

2. **Token budgeting gap**
   - Budget сейчас char-based и линейный.
   - Нет per-source квот, приоритетных слотов и graceful degradation.

3. **Compression gap**
   - Есть summary для логов и memory-by-type, но нет унифицированного компрессора для diff/history/multi-source chunk packs.

4. **Cold memory indexing gap**
   - Нет retrieval-индекса (ключи/теги/temporal windows) для полной истории и старых логов/патчей.

5. **Prompt payload contract gap**
   - Нет формального schema для final prompt payload (sections + provenance + truncation reasons).

6. **Runtime evidence integration gap**
   - Runtime logs пока stub-ориентированные; в контексте нет специального retrieval pipeline для runtime signatures + hardware notes.

---

## 3) Целевая архитектура Context Engine V2

## 3.1 Context sources

- **Hot/active sources**:
  - user task input
  - opened/impacted files
  - latest build/runtime critical events
  - latest diff/status
- **Warm memory sources**:
  - typed project memory (top by importance/time)
  - recent failures + known good fixes
  - project intelligence summary/risky files
- **Cold memory sources**:
  - full project history
  - older memory entries
  - full git history/diffs/checkpoints
  - archived logs

## 3.2 Retrieval flow (проектно-изолированный)

1. Determine **intent** from task type + user input + recent stop reason.
2. Build project-scoped candidate pool from DB + git + logs + intelligence.
3. Normalize into context chunks with metadata:
   - source, timestamp, scope(file/module), severity, memory_type, task linkage.
4. Rank chunks by weighted score:
   - intent match, recency, severity, confidence, file overlap with opened/impacted files.
5. Select top chunks under source quotas.

## 3.3 Ranking flow (первичная версия)

`score = w_intent + w_recency + w_severity + w_overlap + w_memory_importance + w_task_linkage`

- compile diagnosis: higher weight for compile/link/build events + relevant memory types.
- runtime diagnosis: higher weight for runtime categories + hardware_runtime_note/flash_caveat.
- patch planning: higher weight for risky files + known good fix + project invariants.

## 3.4 Compression/summarization flow

- Summarize oversized groups before final assembly:
  - logs -> important summary + ai_ready_context tail
  - memory -> top items by type
  - history/git -> last-N linked to same files/task type
- Preserve provenance markers in compressed chunks (`[src=memory/type=...]`).

## 3.5 Token budgeting flow

Budget split (пример):
- active context: 45%
- warm memory: 35%
- cold references: 15%
- safety buffer/instructions: 5%

Если переполнение:
1) cold trims
2) warm compression
3) active keeps critical-only (severity + overlap)

## 3.6 Final prompt payload flow

1. System/instructions
2. Task + user intent
3. Active context block
4. Warm memory block
5. Cold references block
6. Constraints / stop reasons / safety notes

Каждый блок должен хранить метаданные отбора (why selected, truncated, source ids).

---

## 4) Основные сущности Context Engine V2

- `ContextQuery` (project_id, task_type, user_input, opened_files, limits)
- `ContextChunk` (text, source_type, source_id, score, tokens_estimate, metadata)
- `ContextPlan` (budgets by section, retrieval policy, ranking weights)
- `ContextPayload` (final blocks + provenance + truncation report)

> На Этапе 1 это **дизайн-сущности**, без внедрения новой крупной подсистемы.

---

## 5) Очередность внедрения (итеративно)

1. **Stage A: Retrieval core in existing services**
   - расширить `ContextAssembler` retrieval-aware отбором (без ломки API).
2. **Stage B: Ranking + budget policy**
   - улучшить `ContextBudgetService` до token-aware quotas.
3. **Stage C: Compression adapters**
   - стандартизировать summaries для logs/history/diff/memory.
4. **Stage D: Prompt payload contract**
   - формализовать structured payload, добавить diagnostics/debug info.
5. **Stage E: Runtime evidence hardening**
   - подключить реальный serial runtime ingestion и runtime retrieval.

---

## 6) Ограничения/заметки

- Все retrieval операции строго `project_id`-scoped.
- Local DB + local Git остаются источниками long memory, но в active prompt попадает только ранжированный/сжатый срез.
- Дальнейшее усиление возможно без реархитектуры через расширение существующих `ai/context/prompts/log/history/git` сервисов.

---

## 7) Current implementation status (Stage 8)

Implemented in codebase:
- source registry + retrieval ranking
- log compression and root-cause-oriented reduction
- active/warm/cold memory layering and ranking
- token budget manager and prompt packer
- end-to-end context pipeline wired into chat/diagnosis/build-fix/runtime/patch paths
- debug pack endpoint with explainable report

Hardening checks:
- project-scoped context assembly (`project_id` bound flow)
- dropped fragment reasons and budget debug in packer output
- no full-log sending by default (compressed log context only)

Remaining for future polish:
- production tokenizer alignment per external AI API
- extended end-to-end workload tests under real device/build logs
- frontend debug panel for context report visualization
