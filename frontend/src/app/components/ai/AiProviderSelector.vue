<template>
  <div class="panel">
    <h3>AI Provider</h3>
    <select v-model="store.provider">
      <option value="openai">OpenAI</option>
      <option value="anthropic">Anthropic</option>
      <option value="deepseek">DeepSeek</option>
      <option value="generic">Generic</option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { useAiStore } from '../../store/aiStore'
const store = useAiStore()
</script>
