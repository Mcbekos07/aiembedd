<template>
  <section class="panel">
    <div class="row between">
      <h3>Прозрачность контекста</h3>
      <small>На чём основаны действия агента</small>
    </div>

    <div class="row">
      <select v-model="mode">
        <option value="quick_diagnosis">Быстрая диагностика</option>
        <option value="deep_build_fix">Глубокое исправление build</option>
        <option value="runtime_analysis">Анализ runtime</option>
      </select>
      <Button @click="refresh">Обновить контекст</Button>
    </div>

    <p><strong>Последнее обновление:</strong> {{ store.contextLastUpdatedAt || 'ещё не обновлялся' }}</p>

    <div v-if="report">
      <p><strong>Релевантные файлы:</strong> {{ report.selected_files.length }}</p>
      <ul class="list">
        <li v-for="file in report.selected_files_with_relevance" :key="file.path">
          <strong>{{ file.path }}</strong> (score: {{ file.score.toFixed(1) }})
          <br />
          <small>Причины: {{ file.reasons.join(', ') || '—' }}</small>
        </li>
      </ul>

      <h4>Использованные фрагменты кода</h4>
      <ul class="list">
        <li v-for="frag in codeFragments" :key="frag.id + frag.title">
          {{ frag.title }} — rank={{ Number(frag.rank).toFixed(1) }}
        </li>
      </ul>

      <h4>Важные логи в контексте</h4>
      <ul class="list">
        <li v-for="log in report.selected_logs" :key="log">{{ log }}</li>
      </ul>

      <h4>Использованная память проекта</h4>
      <p>active={{ report.selected_memory_counts.active }}, warm={{ report.selected_memory_counts.warm }}</p>

      <h4>Лимит контекста / budget</h4>
      <pre class="diff-box">{{ budgetSummary }}</pre>

      <h4>Что было отброшено</h4>
      <ul class="list">
        <li v-for="item in droppedPreview" :key="item.id + item.reason">
          {{ item.title }} ({{ item.category }}) — {{ item.reason }}
        </li>
      </ul>
    </div>

    <p v-else class="muted">Пока нет данных контекста. Нажмите «Обновить контекст».</p>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import Button from '../common/Button.vue'
import { useAiStore } from '../../store/aiStore'
import { useProjectStore } from '../../store/projectStore'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId || 0))
const store = useAiStore()
const projectStore = useProjectStore()
const mode = ref<'quick_diagnosis' | 'deep_build_fix' | 'runtime_analysis'>('quick_diagnosis')

const report = computed(() => store.contextReport)
const codeFragments = computed(() => (report.value?.included_fragments || []).filter((item) => item.category === 'code_fragment'))
const droppedPreview = computed(() => (report.value?.dropped_fragments || []).slice(0, 8))
const budgetSummary = computed(() => JSON.stringify(report.value?.budget_debug || {}, null, 2))

async function refresh() {
  if (!projectId.value) return
  await store.loadContextTransparency(projectId.value, {
    mode: mode.value,
    openedFilePath: projectStore.openedFilePath,
    openedFileContent: projectStore.openedFileContent,
  })
}
</script>
