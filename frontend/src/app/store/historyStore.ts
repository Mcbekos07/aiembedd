import { defineStore } from 'pinia'
import { gitApi, type HistoryEvent } from '../services/gitApi'

export const useHistoryStore = defineStore('history', {
  state: () => ({
    events: [] as HistoryEvent[],
  }),
  actions: {
    async fetchHistory(projectId: number): Promise<void> {
      const data = await gitApi.history(projectId)
      this.events = data.items
    },
  },
})
