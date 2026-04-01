<template>
  <div class="panel">
    <h3>Ключевые ошибки</h3>
    <pre class="diff-box">{{ store.errorSummary || 'Ошибок не обнаружено' }}</pre>
  </div>
</template>

<script setup lang="ts">
import { useBuildStore } from '../../store/buildStore'
const store = useBuildStore()
</script>
