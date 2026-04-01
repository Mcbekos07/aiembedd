<template>
  <section class="panel">
    <h2>AI Проектный чат и агент</h2>
    <AiChatPanel :project-id="projectId" />
    <AiTaskPanel :project-id="projectId" />
    <AiTaskHistory />
    <AiActionReview />
    <AiDiffPreview />
    <AiMemoryPanel :project-id="projectId" />
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AiActionReview from '../components/ai/AiActionReview.vue'
import AiChatPanel from '../components/ai/AiChatPanel.vue'
import AiDiffPreview from '../components/ai/AiDiffPreview.vue'
import AiMemoryPanel from '../components/ai/AiMemoryPanel.vue'
import AiTaskHistory from '../components/ai/AiTaskHistory.vue'
import AiTaskPanel from '../components/ai/AiTaskPanel.vue'
import { useAiStore } from '../store/aiStore'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId || 0))
const store = useAiStore()
store.loadChat(projectId.value)
store.loadTasks(projectId.value)
store.loadMemory(projectId.value)
</script>
