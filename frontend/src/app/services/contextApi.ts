import { apiClient } from './apiClient'

export interface ContextPackReport {
  project_id: number
  mode: string
  selected_files: string[]
  selected_files_with_relevance: Array<{ path: string; score: number; reasons: string[] }>
  selected_logs: string[]
  selected_memory_counts: { active: number; warm: number }
  included_fragments: Array<{ id: string; category: string; title: string; rank: number; chars: number }>
  dropped_fragments: Array<{ id: string; category: string; title: string; reason: string; rank: number; chars: number }>
  budget_debug: Record<string, unknown>
  final_size_chars: number
}

export interface ContextPackResponse {
  items: {
    final_context_payload: { prompt_text: string }
    report: ContextPackReport
  }
}

export const contextApi = {
  pack: (projectId: number, payload: { mode: string; task_text: string; opened_file_path?: string; opened_file_content?: string }) =>
    apiClient<ContextPackResponse>(`/ai-context-sources/${projectId}/pack`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
}
