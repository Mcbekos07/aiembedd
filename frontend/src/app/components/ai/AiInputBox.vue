<template>
  <div class="panel form">
    <textarea v-model="text" rows="4" placeholder="Введите вопрос для AI" />
    <Button @click="send">Отправить</Button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from '../common/Button.vue'
import { useAiStore } from '../../store/aiStore'

const props = defineProps<{ projectId: number }>()
const store = useAiStore()
const text = ref('')

async function send() {
  await store.send(props.projectId, text.value)
  text.value = ''
}
</script>
