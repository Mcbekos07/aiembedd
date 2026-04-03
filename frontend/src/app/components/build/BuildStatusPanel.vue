<template>
  <div class="panel">
    <h3>Состояние сборочного контура</h3>
    <p><strong>Текущий job:</strong> {{ store.selectedJobId || '—' }}</p>
    <p><strong>Runtime:</strong> {{ store.runtimeMonitorStatus }}</p>
    <p><strong>Прошивка:</strong> {{ store.flashResult || '—' }}</p>
    <p v-if="store.loadingLogs" class="muted">Загрузка логов…</p>
    <p v-if="store.lastError" class="error">{{ store.lastError }}</p>
  </div>
</template>

<script setup lang="ts">
import { useBuildStore } from '../../store/buildStore'
const store = useBuildStore()
</script>
