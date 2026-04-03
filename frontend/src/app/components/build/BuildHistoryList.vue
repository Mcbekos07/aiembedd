<template>
  <div class="panel">
    <h3>История сборок</h3>
    <p v-if="store.loadingHistory" class="muted">Загрузка истории сборок…</p>
    <p v-else-if="!store.jobs.length" class="muted">Сборки пока не запускались.</p>
    <ul class="list">
      <li v-for="job in store.jobs" :key="job.id">
        <button class="btn" @click="store.fetchLogs(Number(job.id))" :disabled="store.loadingLogs">
          #{{ job.id }} {{ job.action }} — {{ job.status }}
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { useBuildStore } from '../../store/buildStore'
const store = useBuildStore()
</script>
