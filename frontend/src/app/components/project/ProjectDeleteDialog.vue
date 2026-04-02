<template>
  <div class="panel form">
    <h3>Удаление проекта</h3>
    <select v-model="mode">
      <option value="registry_only">Только из реестра</option>
      <option value="registry_with_history">Реестр + история</option>
      <option value="full">Полное удаление</option>
    </select>
    <label><input v-model="confirmed" type="checkbox" /> Подтверждаю удаление</label>
    <Button @click="submit">Удалить</Button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from '../common/Button.vue'
import { useProjectStore } from '../../store/projectStore'

const props = defineProps<{ projectId: number }>()
const projectStore = useProjectStore()
const mode = ref<'registry_only' | 'registry_with_history' | 'full'>('registry_only')
const confirmed = ref(false)

async function submit() {
  await projectStore.deleteProject(props.projectId, mode.value, confirmed.value)
}
</script>
