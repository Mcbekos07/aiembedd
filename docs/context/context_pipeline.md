# Context pipeline (runtime view)

## Runtime-последовательность
1. Вход: `project`, `task_text`, `mode`, `opened_file_*`.
2. `ProjectContextRetrievalService.retrieve(...)` ранжирует files/fragments/memory/history.
3. `ContextSourceRegistry.fetch_source_fragments(...)` добавляет логи, git, memory, prompt-memory и др. источники.
4. `PromptPackerService.pack(...)` применяет приоритеты и budget.
5. Возвращается `prompt_text` + отчёт (`selected_files/logs`, budget_debug, dropped/included fragments).

## Что уже реализовано
- Сквозной pipeline до итогового prompt.
- Отчёт прозрачности контекста для frontend (`selected_files_with_relevance`, `dropped_fragments`, `budget_debug`).
- Учёт task text, opened file, failing files, changed files, history и memory.

## Ограничения / TODO
- Retrieval quality зависит от project intelligence и доступности локальных данных: **partial**.
- Ranking основан на фиксированных весах и heuristic reasons: **partial**.
- Token budgeting грубый, без provider/model-specific tokenization: **partial**.
