<template>
  <form class="panel form" @submit.prevent="submitForm">
    <h3>Новый проект</h3>
    <label>Имя проекта <input v-model="form.name" required /></label>
    <label>Описание <textarea v-model="form.description" rows="3" /></label>
    <label>Платформа <input v-model="form.platform" placeholder="STM32 / ESP32 / RP2040" /></label>
    <label>Система сборки <input v-model="form.build_system" placeholder="cmake / platformio / make" /></label>
    <Button type="submit">Создать проект</Button>
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
  description: '',
  platform: 'custom',
  build_system: 'custom',
  chip: '',
  board: '',
  toolchain: '',
})

async function submitForm() {
  await store.createProject({ ...form })
  await router.push('/ide')
}
</script>
