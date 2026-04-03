import { defineStore } from 'pinia'
import { buildApi, type ImportantLogEvent } from '../services/buildApi'
import { useProjectStore } from './projectStore'
import { useRealtimeStore } from './realtimeStore'

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
    loadingHistory: false,
    loadingLogs: false,
    historyRequestSeq: 0,
    logsRequestSeq: 0,
  }),
  actions: {
    async prepare(projectId: number) {
      useRealtimeStore().ingestLocalEvent('build_started', { action: 'prepare' })
      await buildApi.prepare(projectId)
      await this.fetchHistory(projectId)
    },
    async build(projectId: number) {
      useRealtimeStore().ingestLocalEvent('build_started', { action: 'build' })
      await buildApi.build(projectId)
      await this.fetchHistory(projectId)
    },
    async clean(projectId: number) {
      useRealtimeStore().ingestLocalEvent('build_started', { action: 'clean' })
      await buildApi.clean(projectId)
      await this.fetchHistory(projectId)
    },
    async rebuild(projectId: number) {
      useRealtimeStore().ingestLocalEvent('build_started', { action: 'rebuild' })
      await buildApi.rebuild(projectId)
      await this.fetchHistory(projectId)
    },
    async stop(jobId: number) { await buildApi.stop(jobId) },
    async flash(projectId: number, programmer: string, port: string) {
      useRealtimeStore().ingestLocalEvent('flash_started', { programmer, port })
      const res = await buildApi.flash(projectId, programmer, port, true, false)
      this.flashResult = String((res as { message?: string }).message || '')
      useRealtimeStore().ingestLocalEvent('flash_result', { result: this.flashResult })
    },
    async fetchHistory(projectId: number) {
      const seq = ++this.historyRequestSeq
      this.loadingHistory = true
      const data = await buildApi.history(projectId)
      if (seq !== this.historyRequestSeq) return
      this.jobs = data.items
      this.selectedProjectId = projectId
      if (this.jobs.length > 0) this.selectedJobId = Number(this.jobs[0].id)
      this.loadingHistory = false
    },
    async fetchLogs(jobId: number) {
      const seq = ++this.logsRequestSeq
      this.loadingLogs = true
      const data = await buildApi.logs(jobId)
      if (seq !== this.logsRequestSeq) return
      this.rawLog = data.raw_log
      this.errorSummary = data.error_summary
      this.importantSummary = data.important_summary
      this.rootCause = data.root_cause
      this.repeatedWarnings = data.repeated_warnings
      this.aiReadyContext = data.ai_ready_context
      this.importantEvents = data.important_events
      this.criticalEvents = data.critical_events
      this.selectedJobId = jobId
      this.loadingLogs = false

      if (this.rootCause) useRealtimeStore().ingestLocalEvent('build_failed', { reason: this.rootCause })
      else useRealtimeStore().ingestLocalEvent('build_succeeded', {})
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
        useRealtimeStore().ingestLocalEvent('runtime_event', { message: this.runtimeSummary || this.runtimeRootCause || 'runtime update' })
      }
    },
    async openEventFile(event: ImportantLogEvent) {
      if (!event.file || !this.selectedProjectId) return
      await useProjectStore().openFile(this.selectedProjectId, event.file)
    },
  },
})
