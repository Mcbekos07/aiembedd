<template>
  <div class="panel">
    <h3>Важное</h3>
    <p><strong>Краткая сводка:</strong> {{ store.importantSummary || 'Нет важных событий' }}</p>
    <p><strong>Корневая причина:</strong> {{ store.rootCause || '—' }}</p>

    <h4>Критичные события</h4>
    <p v-if="!store.criticalEvents.length" class="muted">Критичные события не выделены.</p>
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

    <h4>Логи, выбранные агентом в контекст</h4>
    <p v-if="!(aiStore.contextReport?.selected_logs || []).length" class="muted">Агент пока не выбрал логи в контекст.</p>
    <ul class="list">
      <li v-for="item in aiStore.contextReport?.selected_logs || []" :key="item">{{ item }}</li>
    </ul>

    <h4>Повторяющиеся warning</h4>
    <p v-if="!store.repeatedWarnings.length" class="muted">Повторяющихся предупреждений нет.</p>
    <ul class="list">
      <li v-for="line in store.repeatedWarnings" :key="line">{{ line }}</li>
    </ul>

    <details>
      <summary>Контекст для AI</summary>
      <pre class="diff-box">{{ store.aiReadyContext || 'Пока пусто' }}</pre>
    </details>
  </div>
</template>

<script setup lang="ts">
import { useAiStore } from '../../store/aiStore'
import { useBuildStore } from '../../store/buildStore'
const store = useBuildStore()
const aiStore = useAiStore()
</script>
