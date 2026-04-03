<template>
  <form class="panel form" @submit.prevent="submitForm">
    <h3>Импорт локального проекта</h3>
    <label>Имя проекта <input v-model="form.name" required /></label>
    <label>Путь до локального репозитория <input v-model="form.local_path" required /></label>
    <label>Описание <textarea v-model="form.description" rows="3" /></label>
    <Button type="submit">Импортировать</Button>
  </form>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import Button from '../common/Button.vue'
import { useProjectStore } from '../../store/projectStore'

const router = useRouter()
const store = useProjectStore()

const form = reactive({
  name: '',
  local_path: '',
  description: '',
  platform: 'custom',
})

async function submitForm() {
  await store.importLocalProject({ ...form })
  await router.push('/ide')
}
</script>
