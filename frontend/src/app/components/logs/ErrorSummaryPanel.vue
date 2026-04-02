<template>
  <div class="panel">
    <h3>Важное</h3>
    <p><strong>Summary:</strong> {{ store.importantSummary || 'Нет важных событий' }}</p>
    <p><strong>Root cause:</strong> {{ store.rootCause || '—' }}</p>

    <h4>Критичные события</h4>
    <ul class="list">
      <li v-for="event in store.criticalEvents" :key="`${event.row}-${event.message}`">
        <button
          class="btn"
          @click="store.openEventFile(event)"
          :disabled="!event.file"
        >
          [{{ event.stage }}] {{ event.message }}
          <span v-if="event.file"> ({{ event.file }}:{{ event.line || '?' }})</span>
        </button>
      </li>
    </ul>

    <h4>Повторяющиеся warning</h4>
    <ul class="list">
      <li v-for="line in store.repeatedWarnings" :key="line">{{ line }}</li>
    </ul>

    <details>
      <summary>AI-ready context</summary>
      <pre class="diff-box">{{ store.aiReadyContext || 'Пока пусто' }}</pre>
    </details>
  </div>
</template>

<script setup lang="ts">
import { useBuildStore } from '../../store/buildStore'
const store = useBuildStore()
</script>
