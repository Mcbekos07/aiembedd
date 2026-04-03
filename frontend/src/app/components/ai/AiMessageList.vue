<template>
  <div class="panel">
    <h3>Сообщения</h3>
    <ul class="list">
      <li v-for="m in store.messages" :key="m.created_at + m.role"><strong>{{ m.role }}:</strong> {{ m.content }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { useAiStore } from '../../store/aiStore'
const store = useAiStore()
</script>
