<template>
  <div class="panel form">
    <h3>Commit</h3>
    <label>Сообщение коммита <input v-model="message" /></label>
    <Button @click="commit">Сделать commit</Button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from '../common/Button.vue'
import { useGitStore } from '../../store/gitStore'

const props = defineProps<{ projectId: number }>()
const store = useGitStore()
const message = ref('Обновление проекта')

async function commit() {
  await store.commit(props.projectId, message.value)
}
</script>
