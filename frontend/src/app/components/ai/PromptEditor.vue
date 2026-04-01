<template>
  <div class="panel form">
    <h3>Project prompt editor</h3>
    <textarea v-model="store.promptText" rows="8" />
    <Button @click="store.save(projectId)">Сохранить prompt</Button>
  </div>
</template>

<script setup lang="ts">
import Button from '../common/Button.vue'
import { usePromptStore } from '../../store/promptStore'

defineProps<{ projectId: number }>()
const store = usePromptStore()
</script>
