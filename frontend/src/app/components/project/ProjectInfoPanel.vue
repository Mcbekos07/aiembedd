<template>
  <aside class="panel ide-right">
    <h3>Информация о проекте</h3>
    <p>Платформа: {{ project?.platform || '—' }}</p>
    <p>Ветка: {{ project?.current_branch || 'main' }}</p>
    <p>Версия: {{ project?.current_version || '0.1.0' }}</p>
    <QuickActions />
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import QuickActions from '../ide/QuickActions.vue'
import { useProjectStore } from '../../store/projectStore'

const route = useRoute()
const store = useProjectStore()

const project = computed(() => {
  const id = Number(route.params.projectId)
  return store.projects.find((item) => item.id === id)
})
</script>
