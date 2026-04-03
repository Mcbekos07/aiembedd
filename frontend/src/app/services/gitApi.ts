import { apiClient } from './apiClient'

export interface VersionRow {
  version: string
  kind: string
  tag_name: string
  note: string
  created_at: string
}

export interface HistoryEvent {
  id: string
  event_type: string
  title: string
  details: string
  created_at: string
}

export interface AgentCheckpoint {
  id: number
  task_id: number
  checkpoint_type: string
  git_ref: string
  commit_message: string
  status: string
  note: string
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
  listCheckpoints: (projectId: number) => apiClient<{ items: AgentCheckpoint[] }>(`/git/${projectId}/checkpoints`),
  createCheckpoint: (projectId: number, checkpoint_type: string, message: string, task_id = 0, note = '') =>
    apiClient(`/git/${projectId}/checkpoints`, { method: 'POST', body: JSON.stringify({ checkpoint_type, message, task_id, note }) }),
  restoreCheckpoint: (projectId: number, checkpoint_id: number) =>
    apiClient(`/git/${projectId}/checkpoints/restore`, { method: 'POST', body: JSON.stringify({ checkpoint_id }) }),
  suggestCommitMessage: (projectId: number, task_id: number) =>
    apiClient<{ message: string }>(`/git/${projectId}/suggest-commit-message`, { method: 'POST', body: JSON.stringify({ task_id }) }),
  createVersionFromTask: (projectId: number, task_id: number, kind: string, note: string, with_tag: boolean) =>
    apiClient(`/git/${projectId}/version-from-task`, { method: 'POST', body: JSON.stringify({ task_id, kind, note, with_tag }) }),
}
