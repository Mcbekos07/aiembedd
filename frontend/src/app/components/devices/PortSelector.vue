<template>
  <div class="panel">
    <h3>Порт</h3>
    <select v-model="selected">
      <option v-for="port in store.ports" :key="port" :value="port">{{ port }}</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDeviceStore } from '../../store/deviceStore'

const selected = defineModel<string>('port', { default: '/dev/ttyUSB0' })
const store = useDeviceStore()
store.fetchDevices()
ref(selected)
</script>
