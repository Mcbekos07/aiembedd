import { defineStore } from 'pinia'
import { aiApi } from '../services/aiApi'

export const usePromptStore = defineStore('prompt', {
  state: () => ({
    promptText: '',
    versions: [] as Array<{ version: string; created_at: string }>,
  }),
  actions: {
    async load(projectId: number) {
      this.promptText = (await aiApi.getPrompt(projectId)).prompt_text
      this.versions = (await aiApi.promptVersions(projectId)).items
    },
    async save(projectId: number) {
      await aiApi.savePrompt(projectId, this.promptText)
      await this.load(projectId)
    },
  },
})
