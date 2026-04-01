import { apiClient } from './apiClient'

export interface VersionRow {
  version: string
  kind: string
  tag_name: string
  created_at: string
}

export interface HistoryEvent {
  id: string
  event_type: string
  title: string
  details: string
  created_at: string
}

export const gitApi = {
  init: (projectId: number) => apiClient(`/git/${projectId}/init`, { method: 'POST' }),
  diff: (projectId: number) => apiClient<{ output: string }>(`/git/${projectId}/diff`),
  commit: (projectId: number, message: string) =>
    apiClient(`/git/${projectId}/commit`, { method: 'POST', body: JSON.stringify({ message }) }),
  branches: (projectId: number) => apiClient<{ current_branch: string; branches: string[] }>(`/branches/${projectId}`),
  switchBranch: (projectId: number, branch_name: string) =>
    apiClient(`/branches/${projectId}/switch`, { method: 'POST', body: JSON.stringify({ branch_name }) }),
  fetchRemote: (projectId: number) => apiClient(`/remote-git/${projectId}/fetch`, { method: 'POST' }),
  pullRemote: (projectId: number) => apiClient(`/remote-git/${projectId}/pull`, { method: 'POST' }),
  addRemote: (projectId: number, name: string, url: string) =>
    apiClient(`/remote-git/${projectId}/remotes`, { method: 'POST', body: JSON.stringify({ name, url }) }),
  versions: (projectId: number) => apiClient<{ items: VersionRow[] }>(`/versions/${projectId}`),
  createVersion: (projectId: number, kind: string, with_tag: boolean) =>
    apiClient(`/versions/${projectId}`, { method: 'POST', body: JSON.stringify({ kind, with_tag }) }),
  history: (projectId: number) => apiClient<{ items: HistoryEvent[] }>(`/history/${projectId}`),
}
