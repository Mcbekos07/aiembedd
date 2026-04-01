import { apiClient } from './apiClient'

export const aiApi = {
  getPrompt: (projectId: number) => apiClient<{ prompt_text: string }>(`/prompts/${projectId}`),
  savePrompt: (projectId: number, prompt_text: string) => apiClient(`/prompts/${projectId}`, { method: 'POST', body: JSON.stringify({ prompt_text }) }),
  promptVersions: (projectId: number) => apiClient<{ items: Array<{ version: string; created_at: string }> }>(`/prompts/${projectId}/versions`),
  listChat: (projectId: number) => apiClient<{ items: Array<{ role: string; content: string; created_at: string }> }>(`/ai-chat/${projectId}`),
  sendChat: (projectId: number, content: string) => apiClient<{ reply: string }>(`/ai-chat/${projectId}`, { method: 'POST', body: JSON.stringify({ content }) }),
  listMemory: (projectId: number) => apiClient<{ items: Array<{ key: string; value: string; created_at: string }> }>(`/ai-memory/${projectId}`),
  addMemory: (projectId: number, key: string, value: string) => apiClient(`/ai-memory/${projectId}`, { method: 'POST', body: JSON.stringify({ key, value }) }),
  listTasks: (projectId: number) => apiClient<{ items: Array<{ id: string; task_type: string; status: string; created_at: string }> }>(`/ai-tasks/${projectId}`),
  runTask: (projectId: number, task_type: string, input_text: string) =>
    apiClient<{ result: string }>(`/ai-tasks/${projectId}`, { method: 'POST', body: JSON.stringify({ task_type, input_text }) }),
  runAction: (action: string, payload: string) => apiClient<{ result: string }>('/ai-agent/act', { method: 'POST', body: JSON.stringify({ action, payload }) }),
}
