<template>
  <div class="panel">
    <h3>Модель</h3>
    <input v-model="store.model" />
  </div>
</template>

<script setup lang="ts">
import { useAiStore } from '../../store/aiStore'
const store = useAiStore()
</script>
