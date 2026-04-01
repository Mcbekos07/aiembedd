<template>
  <div class="panel">
    <h3>История AI задач</h3>
    <ul class="list"><li v-for="t in store.tasks" :key="t.id">{{ t.task_type }} — {{ t.status }}</li></ul>
  </div>
</template>

<script setup lang="ts">
import { useAiStore } from '../../store/aiStore'
const store = useAiStore()
</script>
