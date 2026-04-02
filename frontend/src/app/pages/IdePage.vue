<template>
  <div class="ide-layout">
    <ProjectSidebar :project-id="projectId" />
    <CodeEditor />
    <div class="panel">
      <ProjectInfoPanel />
      <ProjectIntelligencePanel />
      <QuickActions :project-id="projectId" />
      <GitStatusPanel :project-id="projectId" />
      <BuildControlPanel :project-id="projectId" :programmer="programmer" :port="port" />
      <AiChatPanel :project-id="projectId" />
      <ProjectDeleteDialog :project-id="projectId" />
    </div>
  </div>
  <section class="panel ide-logs">
    <LogConsole />
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AiChatPanel from '../components/ai/AiChatPanel.vue'
import BuildControlPanel from '../components/build/BuildControlPanel.vue'
import GitStatusPanel from '../components/git/GitStatusPanel.vue'
import CodeEditor from '../components/ide/CodeEditor.vue'
import ProjectSidebar from '../components/ide/ProjectSidebar.vue'
import QuickActions from '../components/ide/QuickActions.vue'
import LogConsole from '../components/logs/LogConsole.vue'
import ProjectDeleteDialog from '../components/project/ProjectDeleteDialog.vue'
import ProjectInfoPanel from '../components/project/ProjectInfoPanel.vue'
import ProjectIntelligencePanel from '../components/project/ProjectIntelligencePanel.vue'
import { useProjectStore } from '../store/projectStore'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId || 0))
const programmer = ref('stlink')
const port = ref('/dev/ttyUSB0')
const projectStore = useProjectStore()

watch(projectId, (id) => {
  if (id > 0) {
    void projectStore.loadTree(id)
  }
}, { immediate: true })
</script>
