<template>
  <div class="panel">
    <h3>История AI задач</h3>
    <ul class="list">
      <li
        v-for="t in store.tasks"
        :key="t.id"
        @click="select(t.id)"
        :style="{ cursor: 'pointer', fontWeight: t.id === store.selectedTaskId ? '600' : '400' }"
      >
        {{ t.task_type }} — {{ readableStatus(t.status) }}
      </li>
    </ul>

    <div v-if="selectedTask" class="timeline">
      <p><strong>Output:</strong> {{ selectedTask.output_text || '—' }}</p>
      <h4>Timeline</h4>
      <ul class="list">
        <li v-for="a in selectedActions" :key="a.id">
          <strong>{{ a.action_type }}</strong> — {{ formatPayload(a.payload) }}
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

function readableStatus(status: string) {
  if (status === 'succeeded') return 'успешно'
  if (status === 'failed') return 'ошибка'
  if (status === 'running') return 'в работе'
  if (status === 'queued') return 'в очереди'
  return status
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
