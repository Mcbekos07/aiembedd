<template>
  <div class="panel">
    <h3>Профиль сборки</h3>
    <select v-model="profile">
      <option value="debug">debug</option>
      <option value="release">release</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const profile = ref('debug')
</script>
