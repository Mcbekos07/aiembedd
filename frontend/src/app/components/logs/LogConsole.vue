<template>
  <div class="panel">
    <h3>Сырые логи сборки/runtime</h3>
    <p class="muted">Логи отображаются в оригинале без перевода.</p>
    <p v-if="store.loadingLogs" class="muted">Загрузка логов…</p>
    <pre class="diff-box">{{ store.rawLog || 'Логи пока отсутствуют.' }}</pre>
  </div>
</template>

<script setup lang="ts">
import { useBuildStore } from '../../store/buildStore'
const store = useBuildStore()
</script>
