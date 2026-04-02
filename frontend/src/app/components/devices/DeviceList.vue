<template>
  <div class="panel">
    <h3>USB устройства</h3>
    <Button @click="store.fetchDevices">Сканировать</Button>
    <ul class="list">
      <li v-for="item in store.usbScan" :key="item.id">{{ item.vendor }} / {{ item.product }}</li>
    </ul>
    <h4>USB parser</h4>
    <ul class="list">
      <li v-for="item in store.usbParser" :key="item.id">{{ item.vendor }} / {{ item.product }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import Button from '../common/Button.vue'
import { useDeviceStore } from '../../store/deviceStore'
const store = useDeviceStore()
</script>
