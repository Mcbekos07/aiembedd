<template>
  <div class="panel">
    <h3>Версии prompt</h3>
    <ul class="list"><li v-for="v in store.versions" :key="v.version">{{ v.version }} — {{ v.created_at }}</li></ul>
  </div>
</template>

<script setup lang="ts">
import { usePromptStore } from '../../store/promptStore'
const store = usePromptStore()
</script>
