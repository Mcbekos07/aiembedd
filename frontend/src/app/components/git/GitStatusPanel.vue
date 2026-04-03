<template>
  <div class="panel">
    <h3>Статус Git</h3>
    <p>Текущая ветка: {{ store.currentBranch || '—' }}</p>
    <Button @click="load">Обновить ветки</Button>
  </div>
</template>

<script setup lang="ts">
import Button from '../common/Button.vue'
import { useGitStore } from '../../store/gitStore'

const props = defineProps<{ projectId: number }>()
const store = useGitStore()

async function load() {
  await store.fetchBranches(props.projectId)
}
</script>
