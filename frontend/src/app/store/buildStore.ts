import { defineStore } from 'pinia'
import { buildApi, type ImportantLogEvent } from '../services/buildApi'
import { useProjectStore } from './projectStore'

export const useBuildStore = defineStore('build', {
  state: () => ({
    jobs: [] as Array<{ id: string; action: string; status: string; created_at: string }>,
    selectedJobId: 0,
    selectedProjectId: 0,
    rawLog: '',
    errorSummary: '',
    importantSummary: '',
    rootCause: '',
    repeatedWarnings: [] as string[],
    aiReadyContext: '',
    importantEvents: [] as ImportantLogEvent[],
    criticalEvents: [] as ImportantLogEvent[],
    runtimeMonitorStatus: 'idle',
    runtimeSessionId: 0,
    runtimePort: '',
    runtimeSummary: '',
    runtimeRootCause: '',
    runtimeEventCounts: {} as Record<string, number>,
    flashResult: '',
  }),
  actions: {
    async prepare(projectId: number) { await buildApi.prepare(projectId); await this.fetchHistory(projectId) },
    async build(projectId: number) { await buildApi.build(projectId); await this.fetchHistory(projectId) },
    async clean(projectId: number) { await buildApi.clean(projectId); await this.fetchHistory(projectId) },
    async rebuild(projectId: number) { await buildApi.rebuild(projectId); await this.fetchHistory(projectId) },
    async stop(jobId: number) { await buildApi.stop(jobId) },
    async flash(projectId: number, programmer: string, port: string) {
      const res = await buildApi.flash(projectId, programmer, port, true, false)
      this.flashResult = String((res as { message?: string }).message || '')
    },
    async fetchHistory(projectId: number) {
      const data = await buildApi.history(projectId)
      this.jobs = data.items
      this.selectedProjectId = projectId
      if (this.jobs.length > 0) this.selectedJobId = Number(this.jobs[0].id)
    },
    async fetchLogs(jobId: number) {
      const data = await buildApi.logs(jobId)
      this.rawLog = data.raw_log
      this.errorSummary = data.error_summary
      this.importantSummary = data.important_summary
      this.rootCause = data.root_cause
      this.repeatedWarnings = data.repeated_warnings
      this.aiReadyContext = data.ai_ready_context
      this.importantEvents = data.important_events
      this.criticalEvents = data.critical_events
      this.selectedJobId = jobId
    },
    async refreshRuntime(projectId: number) {
      const status = await buildApi.monitorStatus(projectId)
      this.runtimeMonitorStatus = status.status
      this.runtimeSessionId = status.session?.id ?? 0
      this.runtimePort = status.session?.port ?? ''
      if (this.runtimeSessionId) {
        const logs = await buildApi.monitorLogs(this.runtimeSessionId, 'heartbeat')
        this.runtimeSummary = logs.runtime_summary
        this.runtimeRootCause = logs.root_cause
        this.runtimeEventCounts = logs.event_counts
      }
    },
    async openEventFile(event: ImportantLogEvent) {
      if (!event.file || !this.selectedProjectId) return
      await useProjectStore().openFile(this.selectedProjectId, event.file)
    },
  },
})
