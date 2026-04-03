<template>
  <section class="panel agent-panel">
    <div class="row between">
      <h3>Панель агента</h3>
      <StatusBadge :label="humanReadableAgentStatus" :tone="statusTone" />
    </div>

    <p><strong>Текущая задача:</strong> {{ currentTask?.task_type || 'нет активной задачи' }}</p>
    <p><strong>Текущий шаг:</strong> {{ currentStep }}</p>
    <p><strong>Результат шага:</strong> {{ stepResult }}</p>
    <p><strong>Причина остановки:</strong> {{ stopReason }}</p>
    <p><strong>Нужно подтверждение:</strong> {{ needsConfirmation ? 'да' : 'нет' }}</p>
    <p><strong>Контекст:</strong> {{ contextStatus }}</p>

    <div class="row">
      <Button @click="refresh">Обновить статус</Button>
      <Button v-if="!store.agentRealtimeEnabled" @click="startRealtime">Включить автообновление</Button>
      <Button v-else @click="stopRealtime">Отключить автообновление</Button>
      <Button @click="requestStop">Остановить агента</Button>
      <Button @click="refreshContext">Обновить контекст</Button>
    </div>

    <details>
      <summary>Состояние потока событий</summary>
      <p><strong>Режим:</strong> {{ store.agentRealtimeMode }} (подготовлено для WebSocket, сейчас используется polling)</p>
      <p><strong>Канал:</strong> {{ store.agentEventStreamState }}</p>
      <p><strong>Последняя синхронизация:</strong> {{ store.agentLastSyncAt || 'ещё не было' }}</p>
    </details>

    <p v-if="store.actionResult" class="muted">{{ store.actionResult }}</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Button from '../common/Button.vue'
import StatusBadge from '../common/StatusBadge.vue'
import { useAiStore } from '../../store/aiStore'
import { useProjectStore } from '../../store/projectStore'

const props = defineProps<{ projectId: number }>()
const store = useAiStore()
const projectStore = useProjectStore()

const currentTask = computed(() => store.tasks[0] ?? null)
const currentActions = computed(() => {
  if (!currentTask.value) return []
  return store.taskActions[currentTask.value.id] ?? []
})
const lastAction = computed(() => (currentActions.value.length > 0 ? currentActions.value[currentActions.value.length - 1] : null))

const statusToText = (status: string) => {
  if (status === 'running') return 'анализирует / выполняет шаг'
  if (status === 'queued') return 'в очереди'
  if (status === 'succeeded') return 'завершено'
  if (status === 'failed') return 'ошибка'
  if (status === 'collecting') return 'собирает'
  if (status === 'diagnosing') return 'диагностирует'
  if (status === 'preparing_patch') return 'готовит правку'
  if (status === 'waiting_confirmation') return 'ждёт подтверждения'
  if (status === 'rebuilding') return 'пересобирает'
  if (status === 'flashing') return 'прошивает'
  if (status === 'runtime_observe') return 'наблюдает runtime'
  return status || 'ожидание'
}

const humanReadableAgentStatus = computed(() => {
  if (store.agentStopRequested) return 'остановлен пользователем'
  return statusToText(currentTask.value?.status || '')
})

const statusTone = computed<'ok' | 'warn' | 'info'>(() => {
  if (store.agentStopRequested) return 'warn'
  const status = currentTask.value?.status || ''
  if (status === 'failed') return 'warn'
  if (status === 'succeeded') return 'ok'
  return 'info'
})

const currentStep = computed(() => {
  if (!lastAction.value) return 'шаг ещё не зафиксирован'
  return actionToStep(lastAction.value.action_type)
})

const stepResult = computed(() => {
  const payload = lastAction.value?.payload
  if (!payload) return currentTask.value?.output_text || '—'
  return String(payload.details || payload.message || payload.error_summary || payload.important_summary || currentTask.value?.output_text || '—')
})

const stopReason = computed(() => {
  if (store.agentStopRequested) return 'Остановлено пользователем'
  const payload = lastAction.value?.payload || {}
  return String(payload.stop_reason || payload.runtime_failure_reason || payload.error_summary || '—')
})

const needsConfirmation = computed(() => {
  if (!lastAction.value) return false
  return String(lastAction.value.requires_confirmation || '').toLowerCase() === 'yes'
})

function actionToStep(action: string) {
  if (action.includes('diagnos')) return 'диагностирует'
  if (action.includes('build') || action.includes('compile')) return 'пересобирает'
  if (action.includes('flash')) return 'прошивает'
  if (action.includes('runtime')) return 'наблюдает runtime'
  if (action.includes('patch') || action.includes('diff')) return 'готовит правку'
  if (action.includes('confirm')) return 'ждёт подтверждения'
  return action || 'анализирует'
}

const contextStatus = computed(() => {
  const report = store.contextReport
  if (!report) return 'не загружен'
  return `файлы=${report.selected_files.length}, логи=${report.selected_logs.length}, размер=${report.final_size_chars}`
})

async function refresh() {
  await store.refreshAgent(props.projectId)
}

function startRealtime() {
  store.startAgentRealtime(props.projectId)
}

function stopRealtime() {
  store.stopAgentRealtime()
}

function requestStop() {
  store.requestAgentStop(props.projectId)
}

async function refreshContext() {
  await store.loadContextTransparency(props.projectId, {
    mode: 'quick_diagnosis',
    openedFilePath: projectStore.openedFilePath,
    openedFileContent: projectStore.openedFileContent,
  })
}
</script>
