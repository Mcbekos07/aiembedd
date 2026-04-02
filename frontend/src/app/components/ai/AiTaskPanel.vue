<template>
  <div class="panel form">
    <h3>AI задачи</h3>
    <select v-model="taskType">
      <option value="suggest_code">suggest code</option>
      <option value="review_diff">review diff</option>
      <option value="explain_build_error">explain build error</option>
      <option value="create_version_message">version message</option>
      <option value="dependency_install_plan">dependency plan</option>
      <option value="compile_fix_loop">compile fix loop</option>
      <option value="runtime_observe_loop">runtime observe loop</option>
    </select>
    <textarea v-model="inputText" rows="3" />
    <Button @click="run">Запустить</Button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from '../common/Button.vue'
import { useAiStore } from '../../store/aiStore'

const props = defineProps<{ projectId: number }>()
const store = useAiStore()
const taskType = ref('suggest_code')
const inputText = ref('')

async function run() {
  await store.runTask(props.projectId, taskType.value, inputText.value)
}
</script>
