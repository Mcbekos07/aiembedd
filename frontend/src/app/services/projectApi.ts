import { apiClient } from './apiClient'

export interface ProjectDto {
  id: number
  name: string
  description: string
  path: string
  source_type: string
  platform: string
  chip: string
  board: string
  build_system: string
  toolchain: string
  current_branch: string
  current_version: string
  default_programmer: string
  default_port: string
  ai_provider: string
  ai_model: string
  created_at: string
  updated_at: string
  target?: string
}

export interface CreateProjectPayload {
  name: string
  description: string
  platform: string
  chip: string
  board: string
  build_system: string
  toolchain: string
}

export interface ImportProjectPayload {
  name: string
  local_path: string
  description: string
  platform: string
}


export interface CloneProjectPayload {
  remote_url: string
  project_name: string
}

export const projectApi = {
  list: () => apiClient<ProjectDto[]>('/projects'),
  create: (payload: CreateProjectPayload) =>
    apiClient<ProjectDto>('/projects', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  importLocal: (payload: ImportProjectPayload) =>
    apiClient<ProjectDto>('/projects/import-local', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  cloneRemote: (payload: CloneProjectPayload) =>
    apiClient<{ status: string; message: string }>('/remote-git/clone', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
}
