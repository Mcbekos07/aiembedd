<template>
  <section class="panel ide-v2-shell">
    <header class="ide-v2-header">
      <div>
        <h2>Инженерная IDE (Dual-mode)</h2>
        <p class="muted">Редактируйте вручную, используйте AI-помощь точечно и запускайте агентные задачи без переключения режима.</p>
      </div>
      <div class="row">
        <StatusBadge :label="manualStatus" tone="ok" />
        <StatusBadge :label="agentStatus" :tone="agentTone" />
      </div>
    </header>

    <QuickActions :project-id="projectId" :programmer="programmer" :port="port" />

    <div class="ide-v2-grid">
      <aside class="ide-zone ide-zone-project">
        <h3>Проект и файлы</h3>
        <ProjectSidebar :project-id="projectId" />
      </aside>

      <main class="ide-zone ide-zone-editor">
        <h3>Редактор</h3>
        <CodeEditor />
      </main>

      <aside class="ide-zone ide-zone-agent">
        <h3>AI и агент</h3>
        <AgentPanel :project-id="projectId" />
        <AiChatPanel :project-id="projectId" />
        <AiTaskPanel :project-id="projectId" />
        <AiTaskHistory :project-id="projectId" />
        <AiDiffPreview :project-id="projectId" />
      </aside>

      <aside class="ide-zone ide-zone-context">
        <h3>Контекст и инсайты</h3>
        <ProjectInfoPanel />
        <ProjectIntelligencePanel />
        <GitStatusPanel :project-id="projectId" />
        <BuildControlPanel :project-id="projectId" :programmer="programmer" :port="port" />
        <ErrorSummaryPanel />
      </aside>

      <section class="ide-zone ide-zone-logs">
        <div class="row between">
          <h3>Логи</h3>
          <small>Build/compiler/runtime логи отображаются в оригинале</small>
        </div>
        <LogToolbar />
        <LogConsole />
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AgentPanel from '../components/ai/AgentPanel.vue'
import AiChatPanel from '../components/ai/AiChatPanel.vue'
import AiDiffPreview from '../components/ai/AiDiffPreview.vue'
import AiTaskHistory from '../components/ai/AiTaskHistory.vue'
import AiTaskPanel from '../components/ai/AiTaskPanel.vue'
import BuildControlPanel from '../components/build/BuildControlPanel.vue'
import StatusBadge from '../components/common/StatusBadge.vue'
import GitStatusPanel from '../components/git/GitStatusPanel.vue'
import CodeEditor from '../components/ide/CodeEditor.vue'
import ProjectSidebar from '../components/ide/ProjectSidebar.vue'
import QuickActions from '../components/ide/QuickActions.vue'
import ErrorSummaryPanel from '../components/logs/ErrorSummaryPanel.vue'
import LogConsole from '../components/logs/LogConsole.vue'
import LogToolbar from '../components/logs/LogToolbar.vue'
import ProjectInfoPanel from '../components/project/ProjectInfoPanel.vue'
import ProjectIntelligencePanel from '../components/project/ProjectIntelligencePanel.vue'
import { useAiStore } from '../store/aiStore'
import { useBuildStore } from '../store/buildStore'
import { useProjectStore } from '../store/projectStore'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId || 0))
const programmer = ref('stlink')
const port = ref('/dev/ttyUSB0')
const projectStore = useProjectStore()
const aiStore = useAiStore()
const buildStore = useBuildStore()

const manualStatus = computed(() => (projectStore.openedFilePath ? `Ручное редактирование: ${projectStore.openedFilePath}` : 'Ручное редактирование: файл не открыт'))
const agentStatus = computed(() => {
  const task = aiStore.tasks[0]
  if (!task) return 'Агент: ожидание'
  return `Агент: ${task.status}`
})

const agentTone = computed<'ok' | 'warn' | 'info'>(() => {
  const task = aiStore.tasks[0]
  if (!task) return 'info'
  if (task.status === 'failed') return 'warn'
  if (task.status === 'succeeded') return 'ok'
  return 'info'
})

watch(projectId, (id) => {
  if (id > 0) {
    void projectStore.loadTree(id)
    void buildStore.fetchHistory(id)
    void aiStore.loadTasks(id)
    void aiStore.loadPatches(id)
  }
}, { immediate: true })
</script>
