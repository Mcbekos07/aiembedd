# Context engine (текущее состояние)

## Назначение
Собрать контекст проекта для AI: файлы, логи, память, история, git-сигналы и упаковать в prompt.

## Основные компоненты
- Pipeline: `backend/app/services/context/context_pipeline_service.py`
- Retrieval: `project_context_retrieval_service.py`
- Источники: `context_source_registry.py`
- Prompt packing: `backend/app/services/prompts/prompt_packer_service.py`
- Budget: `backend/app/services/prompts/context_budget_service.py`

## Какие данные уже используются
- Файлы и сниппеты (в т.ч. opened file).
- Build/runtime логи (important/compressed).
- Memory (active/warm + typed memory refs).
- История событий и git commits/diff/status.
- Project intelligence (important/risky/dependency map).

## Формирование prompt
- Собираются fragments с category/rank.
- Применяется приоритизация категорий + budget trimming/truncation.
- Формируется итоговый `prompt_text` с секциями `[SYSTEM]`, `[TASK]`, category blocks.

## Ограничения / TODO
- Retrieval есть, но без отдельного advanced retriever backend (hybrid/vector): **partial**.
- Ranking эвристический (rule/weights), без ML reranker: **partial**.
- Token budgeting символьный (`len/4`), без model-accurate tokenizer: **partial**.
