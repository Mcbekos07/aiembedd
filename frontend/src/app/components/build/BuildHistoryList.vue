<template>
  <div class="panel">
    <h3>История сборок</h3>
    <ul class="list">
      <li v-for="job in store.jobs" :key="job.id">
        <button class="btn" @click="store.fetchLogs(Number(job.id))">#{{ job.id }} {{ job.action }} — {{ job.status }}</button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { useBuildStore } from '../../store/buildStore'
const store = useBuildStore()
</script>
