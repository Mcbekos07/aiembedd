<template>
  <div class="start-grid">
    <ProjectSelector />
    <div class="panel">
      <h2>Быстрый старт</h2>
      <div class="grid-actions">
        <RouterLink class="btn" to="/new-project">Новый проект</RouterLink>
        <RouterLink class="btn" to="/ide">Открыть существующий</RouterLink>
        <RouterLink class="btn" to="/import-project">Импорт из локального Git</RouterLink>
        <RouterLink class="btn" to="/clone-project">Клонировать из Git</RouterLink>
      </div>
    </div>
    <RecentProjects />
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import ProjectSelector from '../components/start/ProjectSelector.vue'
import RecentProjects from '../components/start/RecentProjects.vue'
</script>
