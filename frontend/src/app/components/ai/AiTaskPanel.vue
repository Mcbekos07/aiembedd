<template>
  <div class="panel form">
    <h3>Запуск задач агента</h3>
    <select v-model="taskType">
      <option value="suggest_code">Подсказка по коду</option>
      <option value="review_diff">Ревью diff</option>
      <option value="explain_build_error">Объяснение ошибки сборки</option>
      <option value="create_version_message">Сообщение версии/коммита</option>
      <option value="dependency_install_plan">План установки зависимостей</option>
      <option value="compile_fix_loop">Авто-цикл исправления сборки</option>
      <option value="runtime_observe_loop">Наблюдение runtime</option>
    </select>
    <textarea v-model="inputText" rows="3" placeholder="Опишите цель задачи агента" />
    <div class="row">
      <Button @click="run">Запустить задачу</Button>
      <Button @click="runQuickBuildFix">Быстро исправить build</Button>
    </div>
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

async function runQuickBuildFix() {
  taskType.value = 'compile_fix_loop'
  inputText.value = inputText.value || 'Найди проблему сборки, объясни причину и предложи безопасный патч.'
  await run()
}
</script>
