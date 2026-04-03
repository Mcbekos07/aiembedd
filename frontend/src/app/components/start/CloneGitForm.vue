<template>
  <form class="panel form" @submit.prevent="submitForm">
    <h3>Клонирование Git проекта</h3>
    <label>URL репозитория <input v-model="gitUrl" required /></label>
    <label>Имя проекта <input v-model="projectName" required /></label>
    <Button type="submit">Клонировать</Button>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from '../common/Button.vue'
import { useProjectStore } from '../../store/projectStore'

const gitUrl = ref('')
const projectName = ref('')
const router = useRouter()
const store = useProjectStore()

async function submitForm() {
  await store.cloneProject({ remote_url: gitUrl.value, project_name: projectName.value })
  await router.push('/ide')
}
</script>
