<template>
  <div class="panel form">
    <h3>Agent checkpoints</h3>
    <div class="row">
      <input v-model="message" placeholder="checkpoint message" />
      <Button @click="create">Create checkpoint</Button>
    </div>
    <ul class="list">
      <li v-for="c in store.checkpoints" :key="c.id">
        #{{ c.id }} [{{ c.checkpoint_type }}] task={{ c.task_id }} {{ c.git_ref.slice(0, 8) }} — {{ c.status }}
        <Button @click="restore(c.id)">Restore</Button>
        <Button @click="suggest(c.task_id)" v-if="c.task_id > 0">Suggest commit msg</Button>
        <Button @click="versionFromTask(c.task_id)" v-if="c.task_id > 0">Create version</Button>
      </li>
    </ul>
    <p><strong>Suggested message:</strong> {{ store.suggestedCommitMessage || '—' }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from '../common/Button.vue'
import { useGitStore } from '../../store/gitStore'

const props = defineProps<{ projectId: number }>()
const store = useGitStore()
const message = ref('manual checkpoint')

async function create() {
  await store.createCheckpoint(props.projectId, 'manual', message.value)
}

async function restore(checkpointId: number) {
  await store.restoreCheckpoint(props.projectId, checkpointId)
}

async function suggest(taskId: number) {
  await store.suggestCommitMessage(props.projectId, taskId)
}

async function versionFromTask(taskId: number) {
  await store.createVersionFromTask(props.projectId, taskId, 'patch', `From agent task ${taskId}`, false)
}
</script>
