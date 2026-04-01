<template>
  <div class="panel">
    <h3>Статус build jobs</h3>
    <p>Текущий job: {{ store.selectedJobId || '—' }}</p>
  </div>
</template>

<script setup lang="ts">
import { useBuildStore } from '../../store/buildStore'
const store = useBuildStore()
</script>
