import { apiClient } from './apiClient'

export const buildApi = {
  prepare: (projectId: number) => apiClient(`/builds/${projectId}/prepare`, { method: 'POST' }),
  build: (projectId: number) => apiClient(`/builds/${projectId}/run`, { method: 'POST', body: JSON.stringify({ action: 'build' }) }),
  clean: (projectId: number) => apiClient(`/builds/${projectId}/clean`, { method: 'POST' }),
  rebuild: (projectId: number) => apiClient(`/builds/${projectId}/rebuild`, { method: 'POST' }),
  stop: (jobId: number) => apiClient(`/builds/jobs/${jobId}/stop`, { method: 'POST' }),
  history: (projectId: number) => apiClient<{ items: Array<{ id: string; action: string; status: string; created_at: string }> }>(`/builds/${projectId}/history`),
  logs: (jobId: number) => apiClient<{ raw_log: string; error_summary: string }>(`/logs/build/${jobId}`),
  flash: (projectId: number, programmer: string, port: string) =>
    apiClient(`/flash/${projectId}`, { method: 'POST', body: JSON.stringify({ programmer, port }) }),
}
