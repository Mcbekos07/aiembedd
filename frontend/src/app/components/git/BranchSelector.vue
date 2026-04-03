<template>
  <div class="panel form">
    <h3>Ветки</h3>
    <select v-model="selected">
      <option v-for="branch in store.branches" :key="branch" :value="branch">{{ branch }}</option>
    </select>
    <Button @click="switchBranch">Переключить ветку</Button>
  </div>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue'
import Button from '../common/Button.vue'
import { useGitStore } from '../../store/gitStore'

const props = defineProps<{ projectId: number }>()
const store = useGitStore()
const selected = ref('')

watchEffect(() => {
  if (props.projectId > 0) {
    void store.fetchBranches(props.projectId)
    selected.value = store.currentBranch
  }
})

async function switchBranch() {
  if (!selected.value) return
  await store.switchBranch(props.projectId, selected.value)
}
</script>
