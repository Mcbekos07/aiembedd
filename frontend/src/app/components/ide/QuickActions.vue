<template>
  <div class="panel quick-actions-panel">
    <div class="row between">
      <h3>Панель быстрых действий</h3>
      <small>Ручной режим + AI assist</small>
    </div>

    <div class="grid-actions">
      <Button @click="saveFile">Сохранить</Button>
      <Button @click="buildProject">Собрать</Button>
      <Button @click="flashProject">Прошить</Button>
      <Button @click="explainError">Объяснить ошибку</Button>
      <Button @click="fixWithAi">Исправить через ИИ</Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import Button from '../common/Button.vue'
import { useAiStore } from '../../store/aiStore'
import { useBuildStore } from '../../store/buildStore'
import { useProjectStore } from '../../store/projectStore'

const props = withDefaults(defineProps<{ projectId: number; programmer?: string; port?: string }>(), {
  programmer: 'stlink',
  port: '/dev/ttyUSB0',
})

const projectStore = useProjectStore()
const buildStore = useBuildStore()
const aiStore = useAiStore()

async function saveFile() {
  if (props.projectId <= 0) return
  await projectStore.saveFile(props.projectId)
}

async function buildProject() {
  if (props.projectId <= 0) return
  await buildStore.build(props.projectId)
  if (buildStore.selectedJobId > 0) {
    await buildStore.fetchLogs(buildStore.selectedJobId)
  }
}

async function flashProject() {
  if (props.projectId <= 0) return
  await buildStore.flash(props.projectId, props.programmer, props.port)
  await buildStore.refreshRuntime(props.projectId)
}

async function explainError() {
  if (props.projectId <= 0) return
  await aiStore.runDiagnosis(props.projectId, projectStore.openedFilePath, projectStore.openedFileContent)
}

async function fixWithAi() {
  if (props.projectId <= 0) return
  await aiStore.runTask(props.projectId, 'compile_fix_loop', 'Проанализируй текущую ошибку и предложи безопасное исправление.')
}
</script>
