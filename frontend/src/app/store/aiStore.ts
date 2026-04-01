import { defineStore } from 'pinia'
import { aiApi } from '../services/aiApi'

export const useAiStore = defineStore('ai', {
  state: () => ({
    provider: 'openai',
    model: 'gpt-4.1-mini',
    messages: [] as Array<{ role: string; content: string; created_at: string }>,
    tasks: [] as Array<{ id: string; task_type: string; status: string; created_at: string }>,
    memory: [] as Array<{ key: string; value: string; created_at: string }>,
    actionResult: '',
    tokenBudget: 6000,
  }),
  actions: {
    async loadChat(projectId: number) { this.messages = (await aiApi.listChat(projectId)).items },
    async send(projectId: number, text: string) {
      await aiApi.sendChat(projectId, text)
      await this.loadChat(projectId)
    },
    async loadTasks(projectId: number) { this.tasks = (await aiApi.listTasks(projectId)).items },
    async runTask(projectId: number, taskType: string, inputText: string) {
      await aiApi.runTask(projectId, taskType, inputText)
      await this.loadTasks(projectId)
    },
    async loadMemory(projectId: number) { this.memory = (await aiApi.listMemory(projectId)).items },
    async addMemory(projectId: number, key: string, value: string) {
      await aiApi.addMemory(projectId, key, value)
      await this.loadMemory(projectId)
    },
    async runAction(action: string, payload: string) {
      this.actionResult = (await aiApi.runAction(action, payload)).result
    },
  },
})
