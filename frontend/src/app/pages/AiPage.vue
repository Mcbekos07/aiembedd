<template>
  <section class="panel">
    <h2>AI Проектный чат и агент</h2>
    <AgentPanel :project-id="projectId" />
    <AiChatPanel :project-id="projectId" />
    <AiDiagnosisPanel :project-id="projectId" />
    <AiActionReview :project-id="projectId" />
    <AiDiffPreview :project-id="projectId" />
    <AiTaskPanel :project-id="projectId" />
    <AiTaskHistory :project-id="projectId" />
    <AiMemoryPanel :project-id="projectId" />
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import AgentPanel from '../components/ai/AgentPanel.vue'
import AiActionReview from '../components/ai/AiActionReview.vue'
import AiChatPanel from '../components/ai/AiChatPanel.vue'
import AiDiagnosisPanel from '../components/ai/AiDiagnosisPanel.vue'
import AiDiffPreview from '../components/ai/AiDiffPreview.vue'
import AiMemoryPanel from '../components/ai/AiMemoryPanel.vue'
import AiTaskHistory from '../components/ai/AiTaskHistory.vue'
import AiTaskPanel from '../components/ai/AiTaskPanel.vue'
import { useAiStore } from '../store/aiStore'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId || 0))
const store = useAiStore()

watch(projectId, (id) => {
  if (!id) return
  void store.loadChat(id)
  void store.refreshAgent(id)
  void store.loadMemory(id)
}, { immediate: true })

onBeforeUnmount(() => {
  store.stopAgentRealtime()
})
</script>
