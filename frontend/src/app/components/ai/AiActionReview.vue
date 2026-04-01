<template>
  <div class="panel form">
    <h3>AI action review</h3>
    <select v-model="action">
      <option value="generate_patch">generate patch</option>
      <option value="review_diff">review diff</option>
    </select>
    <textarea v-model="payload" rows="3" />
    <Button @click="run">Выполнить</Button>
    <pre class="diff-box">{{ store.actionResult }}</pre>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from '../common/Button.vue'
import { useAiStore } from '../../store/aiStore'

const store = useAiStore()
const action = ref('generate_patch')
const payload = ref('')

async function run() {
  await store.runAction(action.value, payload.value)
}
</script>
