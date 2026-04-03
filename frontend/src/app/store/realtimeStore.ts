import { defineStore } from 'pinia'
import { wsUrl } from '../services/realtimeApi'
import { useAiStore } from './aiStore'
import { useBuildStore } from './buildStore'

export type RealtimeEventType =
  | 'agent_started'
  | 'agent_step'
  | 'build_started'
  | 'build_failed'
  | 'build_succeeded'
  | 'patch_ready'
  | 'patch_applied'
  | 'flash_started'
  | 'flash_result'
  | 'runtime_event'
  | 'task_finished'
  | 'task_needs_confirmation'

interface RealtimeEvent {
  id: number
  type: RealtimeEventType
  payload: Record<string, unknown>
  at: string
}

type ChannelName = 'ai' | 'builds' | 'logs' | 'monitor'

export const useRealtimeStore = defineStore('realtime', {
  state: () => ({
    projectId: 0,
    token: 0,
    nextId: 1,
    events: [] as RealtimeEvent[],
    sockets: {} as Record<ChannelName, WebSocket | null>,
    channelState: {
      ai: 'idle',
      builds: 'idle',
      logs: 'idle',
      monitor: 'idle',
    } as Record<ChannelName, 'idle' | 'connecting' | 'connected' | 'error'>,
    lastEventAt: '',
    staleUi: false,
  }),
  actions: {
    connect(projectId: number) {
      if (!projectId) return
      if (this.projectId !== projectId) {
        this.disconnect()
      }

      this.projectId = projectId
      this.token += 1
      const token = this.token

      const channels: Array<{ name: ChannelName; path: string }> = [
        { name: 'ai', path: `/ws/ai/${projectId}` },
        { name: 'builds', path: `/ws/builds/${projectId}` },
        { name: 'logs', path: `/ws/logs/${projectId}` },
        { name: 'monitor', path: `/ws/monitor/${projectId}` },
      ]

      channels.forEach(({ name, path }) => {
        this.channelState[name] = 'connecting'
        const socket = new WebSocket(wsUrl(path))
        this.sockets[name] = socket

        socket.onopen = () => {
          if (token !== this.token) return
          this.channelState[name] = 'connected'
          socket.send(JSON.stringify({ kind: 'subscribe', project_id: projectId, channel: name }))
        }

        socket.onmessage = (msg) => {
          if (token !== this.token) return
          const event = this.normalizeIncoming(name, msg.data)
          if (event) this.applyEvent(event)
        }

        socket.onerror = () => {
          if (token !== this.token) return
          this.channelState[name] = 'error'
        }

        socket.onclose = () => {
          if (token !== this.token) return
          if (this.channelState[name] !== 'error') this.channelState[name] = 'idle'
        }
      })
    },

    disconnect() {
      ;(['ai', 'builds', 'logs', 'monitor'] as ChannelName[]).forEach((name) => {
        this.sockets[name]?.close()
        this.sockets[name] = null
        this.channelState[name] = 'idle'
      })
      this.projectId = 0
    },

    ingestLocalEvent(type: RealtimeEventType, payload: Record<string, unknown> = {}) {
      this.applyEvent({
        id: this.nextId++,
        type,
        payload,
        at: new Date().toISOString(),
      })
    },

    normalizeIncoming(channel: ChannelName, raw: string): RealtimeEvent | null {
      let data: Record<string, unknown> = {}
      try {
        data = JSON.parse(raw) as Record<string, unknown>
      } catch {
        data = { raw }
      }

      const explicit = String(data.event || '') as RealtimeEventType
      const known: RealtimeEventType[] = [
        'agent_started',
        'agent_step',
        'build_started',
        'build_failed',
        'build_succeeded',
        'patch_ready',
        'patch_applied',
        'flash_started',
        'flash_result',
        'runtime_event',
        'task_finished',
        'task_needs_confirmation',
      ]

      let type: RealtimeEventType
      if (known.includes(explicit)) {
        type = explicit
      } else if (channel === 'ai') {
        type = 'agent_step'
      } else if (channel === 'builds') {
        type = 'build_started'
      } else if (channel === 'logs' || channel === 'monitor') {
        type = 'runtime_event'
      } else {
        return null
      }

      return {
        id: this.nextId++,
        type,
        payload: data,
        at: new Date().toISOString(),
      }
    },

    applyEvent(event: RealtimeEvent) {
      this.lastEventAt = event.at
      this.staleUi = false
      this.events.unshift(event)
      if (this.events.length > 200) this.events = this.events.slice(0, 200)

      const aiStore = useAiStore()
      const buildStore = useBuildStore()
      const projectId = this.projectId

      switch (event.type) {
        case 'agent_started':
          aiStore.actionResult = 'Агент запущен'
          break
        case 'agent_step':
          aiStore.actionResult = String(event.payload.message || event.payload.payload || 'Агент выполняет шаг')
          void aiStore.refreshAgent(projectId)
          break
        case 'task_needs_confirmation':
          aiStore.actionResult = 'Агент ожидает подтверждения пользователя'
          break
        case 'task_finished':
          aiStore.actionResult = 'Задача агента завершена'
          void aiStore.refreshAgent(projectId)
          void aiStore.loadContextTransparency(projectId)
          break
        case 'patch_ready':
          void aiStore.loadPatches(projectId)
          break
        case 'patch_applied':
          void aiStore.loadPatches(projectId)
          break
        case 'build_started':
          buildStore.runtimeMonitorStatus = 'building'
          void buildStore.fetchHistory(projectId)
          break
        case 'build_failed':
          buildStore.runtimeMonitorStatus = 'failed'
          buildStore.rootCause = String(event.payload.reason || buildStore.rootCause || 'Build failed')
          break
        case 'build_succeeded':
          buildStore.runtimeMonitorStatus = 'succeeded'
          break
        case 'flash_started':
          buildStore.flashResult = 'Прошивка запущена'
          break
        case 'flash_result':
          buildStore.flashResult = String(event.payload.result || event.payload.message || 'Результат прошивки обновлён')
          break
        case 'runtime_event':
          buildStore.runtimeSummary = String(event.payload.message || event.payload.payload || buildStore.runtimeSummary || 'Получено runtime событие')
          break
      }
    },

    markStaleIfNeeded(maxAgeMs = 15000) {
      if (!this.lastEventAt) {
        this.staleUi = true
        return
      }
      const age = Date.now() - new Date(this.lastEventAt).getTime()
      this.staleUi = age > maxAgeMs
    },
  },
})
