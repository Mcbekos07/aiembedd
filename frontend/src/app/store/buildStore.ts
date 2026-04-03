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
    runningAction: '' as '' | 'prepare' | 'build' | 'clean' | 'rebuild' | 'flash',
    lastError: '',
  }),
  actions: {
    async prepare(projectId: number) {
      this.runningAction = 'prepare'
      this.lastError = ''
      useRealtimeStore().ingestLocalEvent('build_started', { action: 'prepare' })
      try {
        await buildApi.prepare(projectId)
        await this.fetchHistory(projectId)
      } catch (error) {
        this.lastError = `Не удалось выполнить prepare: ${String(error)}`
      } finally {
        this.runningAction = ''
      }
    },
    async build(projectId: number) {
      this.runningAction = 'build'
      this.lastError = ''
      useRealtimeStore().ingestLocalEvent('build_started', { action: 'build' })
      try {
        await buildApi.build(projectId)
        await this.fetchHistory(projectId)
      } catch (error) {
        this.lastError = `Не удалось выполнить сборку: ${String(error)}`
      } finally {
        this.runningAction = ''
      }
    },
    async clean(projectId: number) {
      this.runningAction = 'clean'
      this.lastError = ''
      useRealtimeStore().ingestLocalEvent('build_started', { action: 'clean' })
      try {
        await buildApi.clean(projectId)
        await this.fetchHistory(projectId)
      } catch (error) {
        this.lastError = `Не удалось выполнить clean: ${String(error)}`
      } finally {
        this.runningAction = ''
      }
    },
    async rebuild(projectId: number) {
      this.runningAction = 'rebuild'
      this.lastError = ''
      useRealtimeStore().ingestLocalEvent('build_started', { action: 'rebuild' })
      try {
        await buildApi.rebuild(projectId)
        await this.fetchHistory(projectId)
      } catch (error) {
        this.lastError = `Не удалось выполнить rebuild: ${String(error)}`
      } finally {
        this.runningAction = ''
      }
    },
    async stop(jobId: number) { await buildApi.stop(jobId) },
    async flash(projectId: number, programmer: string, port: string) {
      this.runningAction = 'flash'
      this.lastError = ''
      useRealtimeStore().ingestLocalEvent('flash_started', { programmer, port })
      try {
        const res = await buildApi.flash(projectId, programmer, port, true, false)
        this.flashResult = String((res as { message?: string }).message || '')
        useRealtimeStore().ingestLocalEvent('flash_result', { result: this.flashResult })
      } catch (error) {
        this.lastError = `Не удалось выполнить прошивку: ${String(error)}`
      } finally {
        this.runningAction = ''
      }
    },
    async fetchHistory(projectId: number) {
      const seq = ++this.historyRequestSeq
      this.loadingHistory = true
      this.lastError = ''
      try {
        const data = await buildApi.history(projectId)
        if (seq !== this.historyRequestSeq) return
        this.jobs = data.items
        this.selectedProjectId = projectId
        if (this.jobs.length > 0) this.selectedJobId = Number(this.jobs[0].id)
      } catch (error) {
        this.lastError = `Не удалось загрузить историю сборок: ${String(error)}`
      } finally {
        if (seq === this.historyRequestSeq) this.loadingHistory = false
      }
    },
    async fetchLogs(jobId: number) {
      const seq = ++this.logsRequestSeq
      this.loadingLogs = true
      this.lastError = ''
      try {
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

        if (this.rootCause) useRealtimeStore().ingestLocalEvent('build_failed', { reason: this.rootCause })
        else useRealtimeStore().ingestLocalEvent('build_succeeded', {})
      } catch (error) {
        this.lastError = `Не удалось загрузить логи сборки: ${String(error)}`
      } finally {
        if (seq === this.logsRequestSeq) this.loadingLogs = false
      }
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
