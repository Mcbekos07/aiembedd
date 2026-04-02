<template>
  <div class="panel">
    <h3>Программатор</h3>
    <select v-model="selected">
      <option value="stlink">stlink</option>
      <option value="openocd">openocd</option>
      <option value="esptool">esptool</option>
      <option value="avrdude">avrdude</option>
      <option value="custom">custom</option>
    </select>
  </div>
</template>

<script setup lang="ts">
const selected = defineModel<string>('programmer', { default: 'stlink' })
</script>
