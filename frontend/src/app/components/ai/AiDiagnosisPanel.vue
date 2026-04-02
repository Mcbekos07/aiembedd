<template>
  <div class="panel">
    <h3>Диагностика</h3>
    <Button @click="runDiagnosis">Запустить диагностику</Button>

    <div v-if="store.diagnosis" class="form">
      <p><strong>Проблема:</strong> {{ store.diagnosis.problem_summary }}</p>
      <p><strong>Причина:</strong> {{ store.diagnosis.probable_cause }}</p>
      <p><strong>Confidence:</strong> {{ store.diagnosis.confidence_level }}</p>
      <p><strong>Safe auto-fix:</strong> {{ store.diagnosis.safe_auto_fix_possible ? 'yes' : 'no' }}</p>

      <h4>Затронутые файлы</h4>
      <ul class="list">
        <li v-for="file in store.diagnosis.impacted_files" :key="file">{{ file }}</li>
      </ul>

      <h4>Suggested fix plan</h4>
      <ul class="list">
        <li v-for="step in store.diagnosis.recommended_fix_actions" :key="step">{{ step }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Button from '../common/Button.vue'
import { useAiStore } from '../../store/aiStore'
import { useProjectStore } from '../../store/projectStore'

const props = defineProps<{ projectId: number }>()
const store = useAiStore()
const projectStore = useProjectStore()

const openedFilePath = computed(() => projectStore.openedFilePath)
const openedFileContent = computed(() => projectStore.openedFileContent)

async function runDiagnosis() {
  await store.runDiagnosis(props.projectId, openedFilePath.value, openedFileContent.value)
}
</script>
