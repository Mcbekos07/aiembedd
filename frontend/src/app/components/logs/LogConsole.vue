<template>
  <div class="panel">
    <h3>Raw Log</h3>
    <pre class="diff-box">{{ store.rawLog || 'Логи пока отсутствуют' }}</pre>
  </div>
</template>

<script setup lang="ts">
import { useBuildStore } from '../../store/buildStore'
const store = useBuildStore()
</script>
