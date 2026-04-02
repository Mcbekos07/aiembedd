<template>
  <div class="panel form">
    <h3>AI patch proposal</h3>
    <input v-model="reason" placeholder="Причина изменения" />
    <input v-model="summary" placeholder="Краткое описание правки" />
    <input v-model="filePath" placeholder="Файл (например src/main.c)" />
    <textarea v-model="newContent" rows="6" placeholder="Новое содержимое файла" />
    <label><input v-model="dangerous" type="checkbox" /> Массовое/опасное изменение</label>
    <Button @click="propose">Сформировать patch</Button>
    <pre class="diff-box">{{ store.actionResult }}</pre>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from '../common/Button.vue'
import { useAiStore } from '../../store/aiStore'

const props = defineProps<{ projectId: number }>()
const store = useAiStore()
const reason = ref('Fix from diagnosis')
const summary = ref('AI patch proposal')
const filePath = ref('')
const newContent = ref('')
const dangerous = ref(false)

async function propose() {
  if (!filePath.value) return
  await store.proposePatch(props.projectId, reason.value, summary.value, dangerous.value, [{ path: filePath.value, new_content: newContent.value }])
  store.actionResult = 'Patch proposal created'
}
</script>
