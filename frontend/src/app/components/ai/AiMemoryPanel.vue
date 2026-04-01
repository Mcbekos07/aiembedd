<template>
  <div class="panel form">
    <h3>Память проекта</h3>
    <div class="row"><input v-model="keyText" placeholder="ключ" /><input v-model="valText" placeholder="значение" /></div>
    <Button @click="add">Добавить</Button>
    <ul class="list"><li v-for="m in store.memory" :key="m.created_at">{{ m.key }}: {{ m.value }}</li></ul>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from '../common/Button.vue'
import { useAiStore } from '../../store/aiStore'

const props = defineProps<{ projectId: number }>()
const store = useAiStore()
const keyText = ref('')
const valText = ref('')

async function add() {
  await store.addMemory(props.projectId, keyText.value, valText.value)
}
</script>
