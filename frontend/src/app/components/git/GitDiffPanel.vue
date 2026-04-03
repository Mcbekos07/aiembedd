<template>
  <div class="panel">
    <div class="row between">
      <h3>Diff</h3>
      <Button @click="load">Показать diff</Button>
    </div>
    <pre class="diff-box">{{ store.diffOutput || 'Нет изменений или diff не загружен' }}</pre>
  </div>
</template>

<script setup lang="ts">
import Button from '../common/Button.vue'
import { useGitStore } from '../../store/gitStore'

const props = defineProps<{ projectId: number }>()
const store = useGitStore()

async function load() {
  await store.fetchDiff(props.projectId)
}
</script>
