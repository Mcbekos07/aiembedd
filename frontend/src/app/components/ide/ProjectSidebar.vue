<template>
  <aside class="panel ide-left">
    <h3>Проект</h3>
    <p>Навигация и дерево файлов</p>
    <FileTree :project-id="projectId" />
  </aside>
</template>

<script setup lang="ts">
import FileTree from './FileTree.vue'

defineProps<{ projectId: number }>()
</script>
