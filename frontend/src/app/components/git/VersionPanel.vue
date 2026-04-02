<template>
  <div class="panel">
    <h3>Auto versioning</h3>
    <p>Текущая версия: {{ store.currentVersion || '0.1.0' }}</p>
  </div>
</template>

<script setup lang="ts">
import { useGitStore } from '../../store/gitStore'

const store = useGitStore()
defineProps<{ projectId: number }>()
</script>
