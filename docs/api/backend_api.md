# Backend API (текущее состояние)

Базовый префикс API задаётся в настройках (`/api/v1` по умолчанию). Ниже перечислены реальные роуты из кода.

## /projects
| endpoint | метод | параметры | ответ |
|---|---|---|---|
| `/projects` | GET | - | `list[ProjectRead]` |
| `/projects/{project_id}` | GET | `project_id` (path) | `ProjectRead` / 404 |
| `/projects/{project_id}/intelligence` | GET | `project_id` (path), `refresh` (query, bool) | `ProjectIntelligenceRead` |
| `/projects` | POST | `ProjectCreateRequest` (body) | `ProjectRead` (201) |
| `/projects/import-local` | POST | `ProjectImportRequest` (body) | `ProjectRead` (201) |
| `/projects/{project_id}` | DELETE | `project_id` (path), `DeleteRequest{mode,confirmed}` (body) | `MessageResponse` |

## /build (фактически `/builds`)
> Роута `/build` в backend нет; используется `/builds`.

| endpoint | метод | параметры | ответ |
|---|---|---|---|
| `/builds/{project_id}/prepare` | POST | `project_id` | `{status, job_id, message}` |
| `/builds/{project_id}/run` | POST | `project_id`, `BuildActionRequest{action}` | `{status, job_id, error_summary}` |
| `/builds/{project_id}/clean` | POST | `project_id` | `{status, job_id, message}` |
| `/builds/{project_id}/rebuild` | POST | `project_id` | `{status, job_id, message}` |
| `/builds/jobs/{job_id}/stop` | POST | `job_id` | `{status, message}` |
| `/builds/{project_id}/history` | GET | `project_id` | `{status, items[]}` |

## /logs
| endpoint | метод | параметры | ответ |
|---|---|---|---|
| `/logs/build/{job_id}` | GET | `job_id`, `last_n_critical` (query, 1..100) | `{raw_log,error_summary,important_summary,root_cause,repeated_warnings,event_counts,ai_ready_context,critical_events,important_events}` |

## /flash
| endpoint | метод | параметры | ответ |
|---|---|---|---|
| `/flash/{project_id}` | POST | `project_id`, `FlashRequest{programmer?,port,artifact_path?,confirmed,allow_mismatch}` | `{status, message}` |

## /agent (фактические группы: `/ai-tasks`, `/ai-agent`, `/ai-chat`)
| endpoint | метод | параметры | ответ |
|---|---|---|---|
| `/ai-tasks/{project_id}` | GET | `project_id` | `{status, items[]}` |
| `/ai-tasks/{project_id}/{task_id}/actions` | GET | `project_id`, `task_id` | `{status, items[]}` |
| `/ai-tasks/{project_id}` | POST | `TaskRequest{task_type,input_text}` | `{status, result}` |
| `/ai-tasks/{project_id}/diagnose` | POST | `DiagnosisRequest` | `DiagnosisResult` |
| `/ai-agent/act` | POST | `AgentActionRequest{action,payload}` | `{status, result}` |
| `/ai-agent/patches/{project_id}` | GET | `project_id` | `{status, items[]}` |
| `/ai-agent/patches/propose` | POST | `PatchProposalRequest` | `PatchActionResponse` |
| `/ai-agent/patches/{patch_id}/apply` | POST | `patch_id`, `PatchApplyRequest{confirmed}` | `PatchActionResponse` |
| `/ai-agent/patches/{patch_id}/reject` | POST | `patch_id` | `PatchActionResponse` |
| `/ai-agent/patches/{patch_id}/rollback` | POST | `patch_id` | `PatchActionResponse` |
| `/ai-chat/{project_id}` | GET | `project_id` | `{status, items[]}` |
| `/ai-chat/{project_id}` | POST | `ChatRequest{content,mode}` | `{status, reply}` |

## TODO / partial
- Единая публичная OpenAPI-таблица по всем группам: **TODO**.
- Формально зафиксированная версия API-контракта для realtime/agent payload: **partial**.
