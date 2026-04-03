<template>
  <section class="panel">
    <h2>История проекта</h2>
    <ProjectTimeline :project-id="projectId" />
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ProjectTimeline from '../components/history/ProjectTimeline.vue'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId || 0))
</script>
