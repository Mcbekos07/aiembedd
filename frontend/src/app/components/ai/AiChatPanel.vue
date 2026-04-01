<template>
  <section class="panel">
    <AiProviderSelector />
    <AiModelSelector />
    <TokenBudgetPanel />
    <AiMessageList />
    <AiInputBox :project-id="projectId" />
  </section>
</template>

<script setup lang="ts">
import AiInputBox from './AiInputBox.vue'
import AiMessageList from './AiMessageList.vue'
import AiModelSelector from './AiModelSelector.vue'
import AiProviderSelector from './AiProviderSelector.vue'
import TokenBudgetPanel from './TokenBudgetPanel.vue'

defineProps<{ projectId: number }>()
</script>
