<template>
  <div class="panel">
    <h3>Зависимости</h3>
    <ul class="list">
      <li v-for="dep in store.dependencies" :key="dep.name">{{ dep.name }} — {{ dep.status }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { useDeviceStore } from '../../store/deviceStore'
const store = useDeviceStore()
store.fetchEnvironment()
</script>
