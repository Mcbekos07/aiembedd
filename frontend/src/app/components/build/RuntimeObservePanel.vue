<template>
  <div class="panel">
    <h3>Runtime observe</h3>
    <p><strong>Device status:</strong> {{ store.runtimeMonitorStatus }} <span v-if="store.runtimePort">({{ store.runtimePort }})</span></p>
    <p><strong>Flash result:</strong> {{ store.flashResult || '—' }}</p>
    <p><strong>Runtime summary:</strong> {{ store.runtimeSummary || '—' }}</p>
    <p><strong>Runtime failure reason:</strong> {{ store.runtimeRootCause || '—' }}</p>
    <ul class="list">
      <li v-for="(count, type) in store.runtimeEventCounts" :key="type">{{ type }}: {{ count }}</li>
    </ul>
    <Button @click="refresh">Refresh runtime status</Button>
  </div>
</template>

<script setup lang="ts">
import Button from '../common/Button.vue'
import { useBuildStore } from '../../store/buildStore'

const props = defineProps<{ projectId: number }>()
const store = useBuildStore()

async function refresh() {
  await store.refreshRuntime(props.projectId)
}
</script>
