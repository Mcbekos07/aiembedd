<template>
  <section class="panel">
    <h2>Устройства</h2>
    <DeviceList />
    <PortSelector v-model:port="port" />
    <ProgrammerSelector v-model:programmer="programmer" />
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DeviceList from '../components/devices/DeviceList.vue'
import PortSelector from '../components/devices/PortSelector.vue'
import ProgrammerSelector from '../components/devices/ProgrammerSelector.vue'

const port = ref('/dev/ttyUSB0')
const programmer = ref('stlink')
</script>
