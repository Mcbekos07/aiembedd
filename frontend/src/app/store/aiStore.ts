import { defineStore } from 'pinia'
import { aiApi, type DiagnosisResult, type PatchItem, type MemoryItem } from '../services/aiApi'
import { contextApi, type ContextPackReport } from '../services/contextApi'
import { useRealtimeStore } from './realtimeStore'

export const useAiStore = defineStore('ai', {
  state: () => ({
    provider: 'openai',
    model: 'gpt-4.1-mini',
    messages: [] as Array<{ role: string; content: string; created_at: string }>,
    tasks: [] as Array<{ id: string; task_type: string; status: string; input_text: string; output_text: string; created_at: string }>,
    taskActions: {} as Record<string, Array<{ id: number; action_type: string; requires_confirmation: string; payload: Record<string, unknown>; created_at: string }>>,
    selectedTaskId: '',
    memory: [] as MemoryItem[],
    memoryCounts: {} as Record<string, number>,
    memoryTopItems: {} as Record<string, Array<{ title: string; content: string; importance: number }>>,
    actionResult: '',
    tokenBudget: 6000,
    diagnosis: null as DiagnosisResult | null,
    patches: [] as PatchItem[],
    selectedPatchId: 0,
    agentStopRequested: false,
    agentRealtimeEnabled: false,
    agentRealtimeMode: 'polling' as 'polling' | 'websocket',
    agentLastSyncAt: '',
    agentEventStreamState: 'disconnected' as 'disconnected' | 'connecting' | 'connected',
    agentPollHandle: 0,
    contextReport: null as ContextPackReport | null,
    contextPromptPreview: '',
    contextLastUpdatedAt: '',
  }),
  actions: {
    async loadChat(projectId: number) { this.messages = (await aiApi.listChat(projectId)).items },
    async send(projectId: number, text: string) {
      await aiApi.sendChat(projectId, text)
      await this.loadChat(projectId)
    },
    async loadTasks(projectId: number) {
      this.tasks = (await aiApi.listTasks(projectId)).items
      if (!this.selectedTaskId && this.tasks.length > 0) this.selectedTaskId = this.tasks[0].id
    },
    async selectTask(projectId: number, taskId: string) {
      this.selectedTaskId = taskId
      if (!taskId) return
      this.taskActions[taskId] = (await aiApi.listTaskActions(projectId, taskId)).items
    },
    async refreshAgent(projectId: number) {
      await this.loadTasks(projectId)
      if (this.tasks.length > 0) {
        await this.selectTask(projectId, this.tasks[0].id)
      }
      await this.loadPatches(projectId)
      this.agentLastSyncAt = new Date().toISOString()
    },
    async loadContextTransparency(
      projectId: number,
      payload: { mode?: string; taskText?: string; openedFilePath?: string; openedFileContent?: string } = {},
    ) {
      const data = await contextApi.pack(projectId, {
        mode: payload.mode || 'quick_diagnosis',
        task_text: payload.taskText || this.tasks[0]?.input_text || '',
        opened_file_path: payload.openedFilePath,
        opened_file_content: payload.openedFileContent,
      })
      this.contextReport = data.items.report
      this.contextPromptPreview = data.items.final_context_payload.prompt_text
      this.contextLastUpdatedAt = new Date().toISOString()
    },
    startAgentRealtime(projectId: number, intervalMs = 3000) {
      this.stopAgentRealtime()
      this.agentRealtimeEnabled = true
      this.agentEventStreamState = 'connecting'
      void this.refreshAgent(projectId).finally(() => {
        this.agentEventStreamState = 'connected'
      })
      this.agentPollHandle = window.setInterval(() => {
        void this.refreshAgent(projectId)
      }, intervalMs)
    },
    stopAgentRealtime() {
      if (this.agentPollHandle) {
        window.clearInterval(this.agentPollHandle)
      }
      this.agentPollHandle = 0
      this.agentRealtimeEnabled = false
      this.agentEventStreamState = 'disconnected'
    },
    requestAgentStop(projectId: number, reason = 'Остановлено пользователем из панели агента') {
      this.agentStopRequested = true
      this.actionResult = `Запрошена остановка агента: ${reason}`
      void this.refreshAgent(projectId)
    },
    clearAgentStopRequest() {
      this.agentStopRequested = false
    },
    async runTask(projectId: number, taskType: string, inputText: string) {
      this.clearAgentStopRequest()
      useRealtimeStore().ingestLocalEvent('agent_started', { task_type: taskType })
      await aiApi.runTask(projectId, taskType, inputText)
      await this.loadTasks(projectId)
      await this.loadMemory(projectId)
      if (this.tasks.length > 0) {
        await this.selectTask(projectId, this.tasks[0].id)
      }
      useRealtimeStore().ingestLocalEvent('task_finished', { task_type: taskType })
    },
    async runDiagnosis(projectId: number, openedFilePath?: string, openedFileContent?: string) {
      this.clearAgentStopRequest()
      useRealtimeStore().ingestLocalEvent('agent_step', { message: 'Агент выполняет диагностику' })
      this.diagnosis = await aiApi.diagnose(projectId, openedFilePath, openedFileContent)
      await this.loadMemory(projectId)
    },
    async loadMemory(projectId: number) {
      this.memory = (await aiApi.listMemory(projectId)).items
      const knowledge = await aiApi.memoryKnowledge(projectId)
      this.memoryCounts = knowledge.counts
      this.memoryTopItems = knowledge.top_items
    },
    async addMemory(projectId: number, key: string, value: string) {
      await aiApi.addMemory(projectId, key, value)
      await this.loadMemory(projectId)
    },
    async addTypedMemory(projectId: number, memoryType: string, title: string, content: string, importance = 3) {
      await aiApi.addTypedMemory(projectId, memoryType, title, content, importance)
      await this.loadMemory(projectId)
    },
    async runMemoryMaintenance(projectId: number) {
      await aiApi.promoteHistoryMemory(projectId)
      await aiApi.compactMemory(projectId)
      await this.loadMemory(projectId)
    },
    async runAction(action: string, payload: string) {
      this.actionResult = (await aiApi.runAction(action, payload)).result
    },
    async loadPatches(projectId: number) {
      const before = this.patches.length
      this.patches = (await aiApi.listPatches(projectId)).items
      if (this.patches.length > before) useRealtimeStore().ingestLocalEvent('patch_ready', { count: this.patches.length })
      if (this.patches.length > 0) this.selectedPatchId = this.patches[0].id
    },
    async proposePatch(projectId: number, reason: string, summary: string, dangerous: boolean, changes: Array<{ path: string; new_content: string }>) {
      await aiApi.proposePatch({ project_id: projectId, reason, summary, dangerous, changes })
      await this.loadPatches(projectId)
      await this.loadMemory(projectId)
    },
    async applyPatch(projectId: number, patchId: number, confirmed: boolean) {
      await aiApi.applyPatch(patchId, confirmed)
      useRealtimeStore().ingestLocalEvent('patch_applied', { patch_id: patchId })
      await this.loadPatches(projectId)
      await this.loadMemory(projectId)
    },
    async rejectPatch(projectId: number, patchId: number) {
      await aiApi.rejectPatch(patchId)
      await this.loadPatches(projectId)
    },
    async rollbackPatch(projectId: number, patchId: number) {
      await aiApi.rollbackPatch(patchId)
      await this.loadPatches(projectId)
    },
  },
})
