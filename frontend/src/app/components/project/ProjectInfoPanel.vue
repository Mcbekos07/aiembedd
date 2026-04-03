<template>
  <aside class="panel ide-right">
    <h3>Информация о проекте</h3>
    <p><strong>Проект:</strong> {{ project?.name || '—' }}</p>
    <p><strong>Платформа:</strong> {{ project?.platform || '—' }}</p>
    <p><strong>Ветка:</strong> {{ project?.current_branch || 'main' }}</p>
    <p><strong>Версия:</strong> {{ project?.current_version || '0.1.0' }}</p>
    <p><strong>Режим работы:</strong> Ручной + AI assist + агент</p>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '../../store/projectStore'

const route = useRoute()
const store = useProjectStore()

const projectId = computed(() => Number(route.params.projectId))

const project = computed(() => {
  const id = projectId.value
  return store.projects.find((item) => item.id === id)
})
</script>
