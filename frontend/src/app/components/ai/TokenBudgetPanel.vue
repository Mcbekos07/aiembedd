<template>
  <div class="panel">
    <h3>Token budget</h3>
    <p>Лимит контекста: {{ store.tokenBudget }} символов (skeleton).</p>
  </div>
</template>

<script setup lang="ts">
import { useAiStore } from '../../store/aiStore'
const store = useAiStore()
</script>
