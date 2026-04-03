# AIEmbedd V2 Overview

V2 builds on the existing backend/frontend structure and strengthens the agent layer **without rearchitecture**.

## Integrated subsystems
- Project intelligence (`ProjectIntelligenceService`) for important files and dependency map.
- Important logs extraction (`ImportantLogService`) + summaries (`LogSummaryService`).
- Diagnosis flow (`AIDiagnosisService`) using context + memory.
- Patch engine (`AIPatchService`) with safe apply/reject/rollback and pre-patch checkpoints.
- Compile-fix loop and runtime flash-observe loop with timeline actions.
- Project memory V2 (`AIMemoryService`) with typed knowledge and maintenance.
- Git checkpoints + version snapshots linked to agent tasks.

## Readiness checklist
- [x] compile-fix loop ready
- [x] flash-observe loop ready
- [x] memory ready
- [x] checkpointing ready
- [x] project isolation preserved (project_id-scoped services/models)

## Known environment dependencies
- Real toolchains/SDKs and firmware commands.
- Real USB/serial hardware availability on Ubuntu host.
- Configured AI provider API keys/models.
