<template>
  <section class="panel">
    <h2>Prompt проекта</h2>
    <PromptEditor :project-id="projectId" />
    <PromptVersionList />
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import PromptEditor from '../components/ai/PromptEditor.vue'
import PromptVersionList from '../components/ai/PromptVersionList.vue'
import { usePromptStore } from '../store/promptStore'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId || 0))
usePromptStore().load(projectId.value)
</script>
