<template>
  <section class="panel ide-center">
    <h3>Редактор</h3>
    <p>Monaco adapter ready: используется fallback textarea до подключения monaco-loader.</p>
    <textarea v-model="store.openedFileContent" class="editor-placeholder" rows="16" placeholder="// Откройте файл в FileTree" />
  </section>
</template>

<script setup lang="ts">
import { useProjectStore } from '../../store/projectStore'

const store = useProjectStore()
</script>
