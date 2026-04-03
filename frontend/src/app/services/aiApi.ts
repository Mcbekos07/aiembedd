import { apiClient } from './apiClient'

export interface DiagnosisResult {
  problem_summary: string
  probable_cause: string
  impacted_files: string[]
  confidence_level: string
  recommended_fix_actions: string[]
  safe_auto_fix_possible: boolean
}

export interface PatchItem {
  id: number
  status: string
  reason: string
  summary: string
  dangerous: boolean
  files: string[]
  diff_preview: string
  git_status_after_apply: string
}

export interface MemoryItem {
  key: string
  memory_type: string
  title: string
  content: string
  importance: number
  source: string
  created_at: string
}

export const aiApi = {
  getPrompt: (projectId: number) => apiClient<{ prompt_text: string }>(`/prompts/${projectId}`),
  savePrompt: (projectId: number, prompt_text: string) => apiClient(`/prompts/${projectId}`, { method: 'POST', body: JSON.stringify({ prompt_text }) }),
  promptVersions: (projectId: number) => apiClient<{ items: Array<{ version: string; created_at: string }> }>(`/prompts/${projectId}/versions`),
  listChat: (projectId: number) => apiClient<{ items: Array<{ role: string; content: string; created_at: string }> }>(`/ai-chat/${projectId}`),
  sendChat: (projectId: number, content: string) => apiClient<{ reply: string }>(`/ai-chat/${projectId}`, { method: 'POST', body: JSON.stringify({ content }) }),
  listMemory: (projectId: number) => apiClient<{ items: MemoryItem[] }>(`/ai-memory/${projectId}`),
  memoryKnowledge: (projectId: number) => apiClient<{ counts: Record<string, number>; top_items: Record<string, Array<{ title: string; content: string; importance: number }>> }>(`/ai-memory/${projectId}/knowledge`),
  addMemory: (projectId: number, key: string, value: string) => apiClient(`/ai-memory/${projectId}`, { method: 'POST', body: JSON.stringify({ key, value }) }),
  addTypedMemory: (projectId: number, memory_type: string, title: string, content: string, importance: number, source = 'manual') =>
    apiClient(`/ai-memory/${projectId}/typed`, { method: 'POST', body: JSON.stringify({ memory_type, title, content, importance, source }) }),
  compactMemory: (projectId: number) => apiClient<{ removed: number }>(`/ai-memory/${projectId}/maintenance/compact`, { method: 'POST' }),
  promoteHistoryMemory: (projectId: number) => apiClient<{ promoted: number }>(`/ai-memory/${projectId}/maintenance/promote-history`, { method: 'POST' }),
  listTasks: (projectId: number) => apiClient<{ items: Array<{ id: string; task_type: string; status: string; input_text: string; output_text: string; created_at: string }> }>(`/ai-tasks/${projectId}`),
  listTaskActions: (projectId: number, taskId: string) =>
    apiClient<{ items: Array<{ id: number; task_id: number; action_type: string; requires_confirmation: string; payload: Record<string, unknown>; created_at: string }> }>(`/ai-tasks/${projectId}/${taskId}/actions`),
  runTask: (projectId: number, task_type: string, input_text: string) =>
    apiClient<{ result: string }>(`/ai-tasks/${projectId}`, { method: 'POST', body: JSON.stringify({ task_type, input_text }) }),
  diagnose: (projectId: number, opened_file_path?: string, opened_file_content?: string) =>
    apiClient<DiagnosisResult>(`/ai-tasks/${projectId}/diagnose`, {
      method: 'POST',
      body: JSON.stringify({ opened_file_path, opened_file_content }),
    }),
  listPatches: (projectId: number) => apiClient<{ items: PatchItem[] }>(`/ai-agent/patches/${projectId}`),
  proposePatch: (payload: { project_id: number; reason: string; summary: string; dangerous: boolean; changes: Array<{ path: string; new_content: string }> }) =>
    apiClient<{ patch_id: number; status: string; diff_preview: string; files: string[] }>('/ai-agent/patches/propose', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  applyPatch: (patchId: number, confirmed: boolean) =>
    apiClient<{ patch_id: number; status: string; git_status: string }>(`/ai-agent/patches/${patchId}/apply`, {
      method: 'POST',
      body: JSON.stringify({ confirmed }),
    }),
  rejectPatch: (patchId: number) => apiClient<{ patch_id: number; status: string }>(`/ai-agent/patches/${patchId}/reject`, { method: 'POST' }),
  rollbackPatch: (patchId: number) => apiClient<{ patch_id: number; status: string }>(`/ai-agent/patches/${patchId}/rollback`, { method: 'POST' }),
  runAction: (action: string, payload: string) => apiClient<{ result: string }>('/ai-agent/act', { method: 'POST', body: JSON.stringify({ action, payload }) }),
}
