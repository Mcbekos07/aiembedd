<template>
  <div class="panel">
    <div class="row between">
      <h3>Предпросмотр патча агента</h3>
      <small>принять / отклонить / откатить</small>
    </div>

    <ul class="list">
      <li v-for="patch in store.patches" :key="patch.id">
        <button class="btn" @click="store.selectedPatchId = patch.id">
          #{{ patch.id }} {{ readableStatus(patch.status) }} — {{ patch.summary || patch.reason }}
        </button>
      </li>
    </ul>

    <div v-if="selectedPatch">
      <p><strong>Режим патча:</strong> {{ patchMode }}</p>
      <p><strong>Зачем правка:</strong> {{ selectedPatch.reason || '—' }}</p>
      <p><strong>Файлы к изменению:</strong> {{ selectedPatch.files.join(', ') || '—' }}</p>
      <p><strong>Связь с агентом:</strong> {{ relatedAgentStep }}</p>
      <p><strong>Риск:</strong> {{ selectedPatch.dangerous ? 'рискованное изменение (нужно явное подтверждение)' : 'обычный' }}</p>
      <p><strong>Последнее событие:</strong> {{ lastRealtimeEvent }}</p>

      <label v-if="selectedPatch.dangerous" class="row">
        <input v-model="dangerousConfirmed" type="checkbox" />
        Подтверждаю применение рискованного изменения
      </label>

      <details open>
        <summary>Предпросмотр diff по файлам</summary>
        <div v-for="section in diffSections" :key="section.file" class="panel inline-ai-panel">
          <h4>{{ section.file }}</h4>
          <pre class="diff-box">{{ section.content }}</pre>
          <details>
            <summary>Только изменённые строки</summary>
            <pre class="diff-box">{{ section.changedLines.join('\n') || 'Нет изменённых строк' }}</pre>
          </details>
        </div>
      </details>

      <div class="grid-actions">
        <Button @click="applyPatch" :disabled="selectedPatch.dangerous && !dangerousConfirmed">Принять и применить</Button>
        <Button @click="rejectPatch">Отклонить</Button>
        <Button @click="rollbackPatch">Откатить патч</Button>
        <Button @click="restoreLatestCheckpoint" :disabled="!latestCheckpointId">Откат к последнему checkpoint</Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import Button from '../common/Button.vue'
import { useAiStore } from '../../store/aiStore'
import { useGitStore } from '../../store/gitStore'
import { useRealtimeStore } from '../../store/realtimeStore'

const props = defineProps<{ projectId: number }>()
const store = useAiStore()
const gitStore = useGitStore()
const dangerousConfirmed = ref(false)
const realtimeStore = useRealtimeStore()

const selectedPatch = computed(() => store.patches.find((p) => p.id === store.selectedPatchId) || null)

const patchMode = computed(() => {
  if (!selectedPatch.value) return '—'
  const files = selectedPatch.value.files.length
  const lines = selectedPatch.value.diff_preview.split('\n').filter((line) => line.startsWith('+') || line.startsWith('-')).length
  if (selectedPatch.value.dangerous) return 'рискованное изменение'
  if (files > 1) return 'многофайловый патч'
  if (lines <= 40) return 'малый быстрый фикс'
  return 'стандартный патч'
})

const relatedAgentStep = computed(() => {
  const taskId = store.selectedTaskId
  if (!taskId) return 'Шаг не выбран'
  const actions = store.taskActions[taskId] || []
  const last = actions.length > 0 ? actions[actions.length - 1] : null
  if (!last) return `Задача #${taskId}`
  return `Задача #${taskId}, шаг ${last.action_type}`
})

const diffSections = computed(() => {
  const patch = selectedPatch.value
  if (!patch) return []

  const chunks: Array<{ file: string; content: string; changedLines: string[] }> = []
  const lines = patch.diff_preview.split('\n')
  let currentFile = 'unknown'
  let buffer: string[] = []

  const flush = () => {
    if (!buffer.length) return
    chunks.push({
      file: currentFile,
      content: buffer.join('\n'),
      changedLines: buffer.filter((line) => (line.startsWith('+') || line.startsWith('-')) && !line.startsWith('+++') && !line.startsWith('---')),
    })
    buffer = []
  }

  for (const line of lines) {
    if (line.startsWith('diff --git ')) {
      flush()
      const matched = line.match(/ b\/(.+)$/)
      currentFile = matched?.[1] || line
      buffer.push(line)
      continue
    }
    buffer.push(line)
  }

  flush()

  if (!chunks.length) {
    return [
      {
        file: patch.files.join(', ') || 'patch',
        content: patch.diff_preview,
        changedLines: patch.diff_preview
          .split('\n')
          .filter((line) => (line.startsWith('+') || line.startsWith('-')) && !line.startsWith('+++') && !line.startsWith('---')),
      },
    ]
  }

  return chunks
})

const latestCheckpointId = computed(() => gitStore.checkpoints[0]?.id || 0)
const lastRealtimeEvent = computed(() => {
  const ev = realtimeStore.events[0]
  if (!ev) return 'нет'
  return `${ev.type} @ ${ev.at}`
})

watch(() => props.projectId, (id) => {
  dangerousConfirmed.value = false
  if (id > 0) {
    void store.loadPatches(id)
    void gitStore.fetchCheckpoints(id)
  }
}, { immediate: true })

watch(() => store.selectedPatchId, () => {
  dangerousConfirmed.value = false
})

function readableStatus(status: string) {
  if (status === 'applied') return 'применён'
  if (status === 'proposed') return 'предложен'
  if (status === 'rejected') return 'отклонён'
  if (status === 'rolled_back') return 'откачен'
  return status
}

async function applyPatch() {
  if (!selectedPatch.value) return
  await store.applyPatch(props.projectId, selectedPatch.value.id, true)
  await gitStore.fetchCheckpoints(props.projectId)
}

async function rejectPatch() {
  if (!selectedPatch.value) return
  await store.rejectPatch(props.projectId, selectedPatch.value.id)
}

async function rollbackPatch() {
  if (!selectedPatch.value) return
  await store.rollbackPatch(props.projectId, selectedPatch.value.id)
  await gitStore.fetchCheckpoints(props.projectId)
}

async function restoreLatestCheckpoint() {
  if (!latestCheckpointId.value) return
  await gitStore.restoreCheckpoint(props.projectId, latestCheckpointId.value)
  await store.loadPatches(props.projectId)
}
</script>
