import { apiClient } from './apiClient'

export interface ImportantLogEvent {
  row: number
  stage: string
  error_type: string
  severity: string
  message: string
  file: string | null
  line: number | null
  raw: string
}

export interface BuildLogsDto {
  raw_log: string
  error_summary: string
  important_summary: string
  root_cause: string
  repeated_warnings: string[]
  event_counts: Record<string, number>
  ai_ready_context: string
  critical_events: ImportantLogEvent[]
  important_events: ImportantLogEvent[]
}

export const buildApi = {
  prepare: (projectId: number) => apiClient(`/builds/${projectId}/prepare`, { method: 'POST' }),
  build: (projectId: number) => apiClient(`/builds/${projectId}/run`, { method: 'POST', body: JSON.stringify({ action: 'build' }) }),
  clean: (projectId: number) => apiClient(`/builds/${projectId}/clean`, { method: 'POST' }),
  rebuild: (projectId: number) => apiClient(`/builds/${projectId}/rebuild`, { method: 'POST' }),
  stop: (jobId: number) => apiClient(`/builds/jobs/${jobId}/stop`, { method: 'POST' }),
  history: (projectId: number) => apiClient<{ items: Array<{ id: string; action: string; status: string; created_at: string }> }>(`/builds/${projectId}/history`),
  logs: (jobId: number) => apiClient<BuildLogsDto>(`/logs/build/${jobId}`),
  flash: (projectId: number, programmer: string, port: string, confirmed = true, allowMismatch = false) =>
    apiClient(`/flash/${projectId}`, { method: 'POST', body: JSON.stringify({ programmer, port, confirmed, allow_mismatch: allowMismatch }) }),
  monitorStatus: (projectId: number) => apiClient<{ status: string; session: null | { id: number; port: string; baudrate: string; created_at: string } }>(`/monitor/${projectId}/status`),
  monitorLogs: (sessionId: number, _expectedOutput = '') => apiClient<{ raw_log: string; runtime_summary: string; root_cause: string; event_counts: Record<string, number> }>(`/monitor/sessions/${sessionId}/logs`),
}
