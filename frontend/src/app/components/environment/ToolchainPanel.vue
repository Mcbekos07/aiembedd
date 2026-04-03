<template>
  <div class="panel">
    <h3>Toolchains</h3>
    <p>Реестр: {{ store.toolchains.join(', ') }}</p>
    <ul class="list">
      <li v-for="item in store.toolchainStates" :key="item.name">{{ item.name }} — {{ item.status }}</li>
    </ul>
    <h4>Пути окружения</h4>
    <ul class="list">
      <li v-for="(value, key) in store.environmentPaths" :key="key">{{ key }}: {{ value }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { useDeviceStore } from '../../store/deviceStore'
const store = useDeviceStore()
store.fetchEnvironment()
</script>
