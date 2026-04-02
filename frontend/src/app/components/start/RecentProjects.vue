<template>
  <div class="panel">
    <div class="row between">
      <h3>Последние проекты</h3>
      <StatusBadge :label="store.loading ? 'Загрузка' : 'Готово'" tone="info" />
    </div>
    <p v-if="store.error" class="error">{{ store.error }}</p>
    <ul v-else class="list">
      <li v-for="project in store.projects" :key="project.id" class="list-item">
        <RouterLink :to="`/ide/${project.id}`">{{ project.name }}</RouterLink>
        <small>{{ project.platform || project.target || 'custom' }}</small>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import StatusBadge from '../common/StatusBadge.vue'
import { useProjectStore } from '../../store/projectStore'

const store = useProjectStore()

onMounted(() => {
  if (!store.projects.length) {
    void store.fetchProjects()
  }
})
</script>
