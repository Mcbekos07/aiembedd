<template>
  <section class="panel ide-center">
    <div class="row between">
      <h3>Редактор</h3>
      <small>Ручное редактирование + inline AI assist</small>
    </div>

    <p class="muted">Monaco adapter ready: используется fallback textarea до подключения monaco-loader.</p>

    <textarea
      ref="editorRef"
      v-model="store.openedFileContent"
      class="editor-placeholder"
      rows="16"
      placeholder="// Откройте файл в FileTree"
      @mouseup="captureSelection"
      @keyup="captureSelection"
      @select="captureSelection"
    />

    <section class="panel inline-ai-panel">
      <div class="row between">
        <h4>Inline AI действия</h4>
        <small>Точечная помощь без полного агентного цикла</small>
      </div>

      <p><strong>Файл:</strong> {{ store.openedFilePath || 'не открыт' }}</p>
      <p><strong>Выделение:</strong> {{ selectionInfo }}</p>
      <p><strong>Контекст агента:</strong> {{ contextQuickSummary }}</p>

      <div class="grid-actions">
        <Button @click="runInlineAction('explain_selection')" :disabled="!canRunWithSelection">Объяснить выделение</Button>
        <Button @click="runInlineAction('fix_selection')" :disabled="!canRunWithSelection">Исправить текущий фрагмент</Button>
        <Button @click="runInlineAction('optimize_selection')" :disabled="!canRunWithSelection">Оптимизировать</Button>
        <Button @click="runInlineAction('generate_for_file')" :disabled="!store.openedFilePath">Сгенерировать по файлу</Button>
        <Button @click="runInlineAction('find_error_cause')" :disabled="!hasErrorContext">Найти причину ошибки</Button>
        <Button @click="runInlineAction('explain_log')" :disabled="!hasLogContext">Объяснить по логу</Button>
      </div>

      <details v-if="selectedText">
        <summary>Показать выделенный фрагмент</summary>
        <pre class="diff-box">{{ selectedText }}</pre>
      </details>

      <div v-if="inlineResponse" class="inline-ai-response">
        <h4>Ответ inline AI</h4>
        <pre class="diff-box">{{ inlineResponse }}</pre>
        <div class="row">
          <Button @click="replaceSelectionWithResponse" :disabled="!canRunWithSelection">Заменить выделение ответом</Button>
          <Button @click="appendResponseToFile" :disabled="!store.openedFilePath">Добавить ответ в конец файла</Button>
        </div>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import Button from '../common/Button.vue'
import { useAiStore } from '../../store/aiStore'
import { useBuildStore } from '../../store/buildStore'
import { useProjectStore } from '../../store/projectStore'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId || 0))
const store = useProjectStore()
const aiStore = useAiStore()
const buildStore = useBuildStore()

const editorRef = ref<HTMLTextAreaElement | null>(null)
const selectionStart = ref(0)
const selectionEnd = ref(0)
const inlineResponse = ref('')

const selectedText = computed(() => {
  if (!store.openedFileContent) return ''
  if (selectionEnd.value <= selectionStart.value) return ''
  return store.openedFileContent.slice(selectionStart.value, selectionEnd.value)
})

const selectionInfo = computed(() => {
  if (!selectedText.value) return 'нет выделения'
  return `символы ${selectionStart.value}-${selectionEnd.value} (${selectedText.value.length} симв.)`
})

const canRunWithSelection = computed(() => !!selectedText.value && !!store.openedFilePath && projectId.value > 0)
const hasErrorContext = computed(() => !!buildStore.rootCause || !!buildStore.errorSummary)
const hasLogContext = computed(() => !!buildStore.importantSummary || !!buildStore.rawLog)
const contextQuickSummary = computed(() => {
  const report = aiStore.contextReport
  if (!report) return 'ещё не загружен'
  return `файлы=${report.selected_files.length}, логи=${report.selected_logs.length}, память(active/warm)=${report.selected_memory_counts.active}/${report.selected_memory_counts.warm}`
})

function captureSelection() {
  const editor = editorRef.value
  if (!editor) return
  selectionStart.value = editor.selectionStart || 0
  selectionEnd.value = editor.selectionEnd || 0
}

function buildPrompt(action: string): string {
  const header = [
    `INLINE_AI_ACTION=${action}`,
    `FILE=${store.openedFilePath || 'unknown'}`,
    `SELECTION_RANGE=${selectionStart.value}-${selectionEnd.value}`,
  ]

  const fileContext = store.openedFileContent ? `\n[ТЕКУЩИЙ ФАЙЛ]\n${store.openedFileContent.slice(0, 6000)}` : ''
  const selectionContext = selectedText.value ? `\n[ВЫДЕЛЕНИЕ]\n${selectedText.value}` : ''
  const errorContext = hasErrorContext.value
    ? `\n[ОШИБКА]\nroot_cause=${buildStore.rootCause || '-'}\nerror_summary=${buildStore.errorSummary || '-'}`
    : ''
  const logContext = hasLogContext.value
    ? `\n[ЛОГ-КОНТЕКСТ]\nimportant_summary=${buildStore.importantSummary || '-'}\nraw_log_excerpt=${(buildStore.rawLog || '').slice(0, 2000)}`
    : ''

  const instruction =
    '\nДай короткий инженерный ответ на русском. Если предлагаешь изменение, сначала объясни почему, затем покажи конкретный фрагмент кода без скрытых шагов.'

  return `${header.join('\n')}${selectionContext}${fileContext}${errorContext}${logContext}${instruction}`
}

async function runInlineAction(action: string) {
  if (projectId.value <= 0) return
  const prompt = buildPrompt(action)
  await aiStore.send(projectId.value, prompt)
  await aiStore.loadContextTransparency(projectId.value, {
    mode: 'quick_diagnosis',
    taskText: `inline:${action}`,
    openedFilePath: store.openedFilePath,
    openedFileContent: store.openedFileContent,
  })
  const assistantMessage = [...aiStore.messages].reverse().find((item) => item.role === 'assistant')
  inlineResponse.value = assistantMessage?.content || 'AI не вернул ответ'
}

function replaceSelectionWithResponse() {
  if (!selectedText.value || !inlineResponse.value) return
  const before = store.openedFileContent.slice(0, selectionStart.value)
  const after = store.openedFileContent.slice(selectionEnd.value)
  store.openedFileContent = `${before}${inlineResponse.value}${after}`
  selectionEnd.value = selectionStart.value + inlineResponse.value.length
}

function appendResponseToFile() {
  if (!inlineResponse.value) return
  store.openedFileContent = `${store.openedFileContent}\n\n/* Inline AI suggestion */\n${inlineResponse.value}`
}
</script>
