import { apiClient } from './apiClient'

export interface ProjectIntelligenceDto {
  project_id: number
  summary: string
  architectural_notes: string
  important_files: string[]
  risky_files: string[]
  known_build_paths: string[]
  entry_points: string[]
  dependency_map: Record<string, string[]>
  file_classification: Record<string, string>
}

export const projectIntelligenceApi = {
  get: (projectId: number) => apiClient<ProjectIntelligenceDto>(`/projects/${projectId}/intelligence`),
}
