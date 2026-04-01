<template>
  <div class="panel">
    <div class="row between">
      <h3>Timeline</h3>
      <Button @click="load">Обновить</Button>
    </div>
    <ul class="list">
      <li v-for="event in historyStore.events" :key="event.id">
        <strong>{{ event.title }}</strong> — {{ event.details }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import Button from '../common/Button.vue'
import { useHistoryStore } from '../../store/historyStore'

const props = defineProps<{ projectId: number }>()
const historyStore = useHistoryStore()

async function load() {
  await historyStore.fetchHistory(props.projectId)
}
</script>
