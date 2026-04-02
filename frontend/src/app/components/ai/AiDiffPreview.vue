<template>
  <div class="panel">
    <h3>Diff preview</h3>
    <ul class="list">
      <li v-for="patch in store.patches" :key="patch.id">
        <button class="btn" @click="store.selectedPatchId = patch.id">#{{ patch.id }} {{ patch.status }} — {{ patch.summary || patch.reason }}</button>
      </li>
    </ul>

    <div v-if="selectedPatch">
      <p><strong>Files:</strong> {{ selectedPatch.files.join(', ') }}</p>
      <p><strong>Reason:</strong> {{ selectedPatch.reason }}</p>
      <pre class="diff-box">{{ selectedPatch.diff_preview }}</pre>
      <div class="grid-actions">
        <Button @click="applyPatch">Approve & apply</Button>
        <Button @click="rejectPatch">Reject</Button>
        <Button @click="rollbackPatch">Rollback</Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import Button from '../common/Button.vue'
import { useAiStore } from '../../store/aiStore'

const props = defineProps<{ projectId: number }>()
const store = useAiStore()

const selectedPatch = computed(() => store.patches.find((p) => p.id === store.selectedPatchId) || null)

watch(() => props.projectId, (id) => {
  if (id > 0) void store.loadPatches(id)
}, { immediate: true })

async function applyPatch() {
  if (!selectedPatch.value) return
  await store.applyPatch(props.projectId, selectedPatch.value.id, true)
}

async function rejectPatch() {
  if (!selectedPatch.value) return
  await store.rejectPatch(props.projectId, selectedPatch.value.id)
}

async function rollbackPatch() {
  if (!selectedPatch.value) return
  await store.rollbackPatch(props.projectId, selectedPatch.value.id)
}
</script>
