import { apiClient } from './apiClient'

export const fileApi = {
  tree: (projectId: number) => apiClient<{ items: Array<{ path: string; type: string }> }>(`/files/${projectId}/tree`),
  read: (projectId: number, path: string) => apiClient<{ content: string }>(`/files/${projectId}/read`, { method: 'POST', body: JSON.stringify({ path }) }),
  save: (projectId: number, path: string, content: string) => apiClient(`/files/${projectId}/save`, { method: 'POST', body: JSON.stringify({ path, content }) }),
  rename: (projectId: number, old_path: string, new_path: string) => apiClient(`/files/${projectId}/rename`, { method: 'POST', body: JSON.stringify({ old_path, new_path }) }),
  delete: (projectId: number, path: string) => apiClient(`/files/${projectId}/delete`, { method: 'POST', body: JSON.stringify({ path }) }),
  create: (projectId: number, path: string, kind: 'file' | 'folder') => apiClient(`/files/${projectId}/create`, { method: 'POST', body: JSON.stringify({ path, kind }) }),
}
