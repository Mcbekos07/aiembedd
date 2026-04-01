import { defineStore } from 'pinia'
import { buildApi } from '../services/buildApi'

export const useBuildStore = defineStore('build', {
  state: () => ({
    jobs: [] as Array<{ id: string; action: string; status: string; created_at: string }>,
    selectedJobId: 0,
    rawLog: '',
    errorSummary: '',
  }),
  actions: {
    async prepare(projectId: number) { await buildApi.prepare(projectId); await this.fetchHistory(projectId) },
    async build(projectId: number) { await buildApi.build(projectId); await this.fetchHistory(projectId) },
    async clean(projectId: number) { await buildApi.clean(projectId); await this.fetchHistory(projectId) },
    async rebuild(projectId: number) { await buildApi.rebuild(projectId); await this.fetchHistory(projectId) },
    async stop(jobId: number) { await buildApi.stop(jobId) },
    async flash(projectId: number, programmer: string, port: string) { await buildApi.flash(projectId, programmer, port) },
    async fetchHistory(projectId: number) {
      const data = await buildApi.history(projectId)
      this.jobs = data.items
      if (this.jobs.length > 0) this.selectedJobId = Number(this.jobs[0].id)
    },
    async fetchLogs(jobId: number) {
      const data = await buildApi.logs(jobId)
      this.rawLog = data.raw_log
      this.errorSummary = data.error_summary
      this.selectedJobId = jobId
    },
  },
})
