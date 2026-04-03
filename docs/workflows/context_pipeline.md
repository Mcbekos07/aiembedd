# Context Pipeline (E2E)

## Purpose
Unified project-scoped context assembly for AI calls.

## Steps
1. Receive task context (`task_text`, `mode`, opened file context).
2. Retrieve top project fragments (`ProjectContextRetrievalService`).
3. Collect compressed log sources (`ContextSourceRegistry`).
4. Fetch active/warm memory (`AIMemoryService`).
5. Pack with token budget (`PromptPackerService` + `TokenBudgetManager`).
6. Return:
   - `prompt_text`
   - context report (selected/dropped fragments, relevance, budget usage).

## Integration points
- Chat flow (`AIChatService`).
- Diagnosis flow (`AIDiagnosisService`).
- Build-fix/runtime loops (pipeline report attached to task actions).
- Patch proposal flow (`AIPatchService`).
- Debug endpoint: `POST /api/v1/ai-context-sources/{project_id}/pack`.
