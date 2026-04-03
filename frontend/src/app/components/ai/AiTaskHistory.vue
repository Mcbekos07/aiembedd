<template>
  <div class="panel">
    <div class="row between">
      <h3>Таймлайн агента</h3>
      <small>Операционные шаги по выбранной задаче</small>
    </div>

    <ul class="list">
      <li
        v-for="t in store.tasks"
        :key="t.id"
        @click="select(t.id)"
        :style="{ cursor: 'pointer', fontWeight: t.id === store.selectedTaskId ? '600' : '400' }"
      >
        #{{ t.id }} {{ readableTaskType(t.task_type) }} — {{ readableStatus(t.status) }}
      </li>
    </ul>

    <div v-if="selectedTask" class="timeline">
      <p><strong>Итог задачи:</strong> {{ selectedTask.output_text || '—' }}</p>
      <p><strong>Статус:</strong> {{ readableStatus(selectedTask.status) }}</p>
      <h4>Шаги</h4>
      <ul class="list">
        <li v-for="a in selectedActions" :key="a.id">
          <strong>{{ stepName(a.action_type) }}</strong>
          — {{ formatPayload(a.payload) }}
          <span v-if="needsConfirmation(a)"> (требует подтверждения)</span>
          <span v-if="findStopReason(a.payload)"> | причина остановки: {{ findStopReason(a.payload) }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAiStore } from '../../store/aiStore'

const props = defineProps<{ projectId: number }>()
const store = useAiStore()

const selectedTask = computed(() => store.tasks.find((t) => t.id === store.selectedTaskId) ?? null)
const selectedActions = computed(() => (store.selectedTaskId ? (store.taskActions[store.selectedTaskId] ?? []) : []))

async function select(taskId: string) {
  await store.selectTask(props.projectId, taskId)
}

function readableTaskType(taskType: string) {
  if (taskType === 'compile_fix_loop') return 'агентный цикл исправления сборки'
  if (taskType === 'runtime_observe_loop') return 'агентное наблюдение runtime'
  if (taskType === 'explain_build_error') return 'объяснение ошибки сборки'
  if (taskType === 'review_diff') return 'ревью diff'
  if (taskType === 'suggest_code') return 'подсказка по коду'
  return taskType
}

function readableStatus(status: string) {
  if (status === 'succeeded') return 'завершено'
  if (status === 'failed') return 'ошибка'
  if (status === 'running') return 'анализирует/выполняет'
  if (status === 'queued') return 'в очереди'
  if (status === 'collecting') return 'собирает'
  if (status === 'diagnosing') return 'диагностирует'
  if (status === 'preparing_patch') return 'готовит правку'
  if (status === 'waiting_confirmation') return 'ждёт подтверждения'
  if (status === 'rebuilding') return 'пересобирает'
  if (status === 'flashing') return 'прошивает'
  if (status === 'runtime_observe') return 'наблюдает runtime'
  return status
}

function stepName(actionType: string) {
  if (actionType.includes('diagnos')) return 'Диагностика'
  if (actionType.includes('build') || actionType.includes('compile')) return 'Сборка'
  if (actionType.includes('patch') || actionType.includes('diff')) return 'Подготовка правки'
  if (actionType.includes('flash')) return 'Прошивка'
  if (actionType.includes('runtime')) return 'Наблюдение runtime'
  if (actionType.includes('confirm')) return 'Ожидание подтверждения'
  return actionType
}

function needsConfirmation(action: { requires_confirmation: string }) {
  return String(action.requires_confirmation).toLowerCase() === 'yes'
}

function findStopReason(payload: Record<string, unknown>) {
  return String(payload.stop_reason || payload.runtime_failure_reason || payload.error_summary || '')
}

function formatPayload(payload: Record<string, unknown>) {
  if (payload.stop_reason) return `stop_reason=${String(payload.stop_reason)}; details=${String(payload.details || '')}`
  if (payload.runtime_failure_reason) return `runtime_failure=${String(payload.runtime_failure_reason)}; summary=${String(payload.important_summary || '')}`
  if (payload.error_summary) return `build=${String(payload.build_status || '')}; error=${String(payload.error_summary || '')}`
  if (payload.message) return String(payload.message)
  if (payload.version) return `version snapshot=${String(payload.version)}`
  return JSON.stringify(payload)
}
</script>
