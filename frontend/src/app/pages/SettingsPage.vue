<template>
  <section class="panel form">
    <h2>Настройки IDE</h2>
    <label>Тема <input v-model="theme" /></label>
    <label>Язык <input v-model="language" /></label>
    <label>Git settings <input v-model="git" /></label>
    <label>Build settings <input v-model="build" /></label>
    <label>AI settings <input v-model="ai" /></label>
    <label>Security settings <input v-model="security" /></label>
    <button class="btn" @click="save">Сохранить</button>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const theme = ref('')
const language = ref('ru')
const git = ref('')
const build = ref('')
const ai = ref('')
const security = ref('')

async function load() {
  const response = await fetch(`${apiBase}/settings`)
  if (!response.ok) return
  const data = await response.json()
  theme.value = data.categories?.theme || ''
  language.value = data.categories?.language || 'ru'
  git.value = data.categories?.git || ''
  build.value = data.categories?.build || ''
  ai.value = data.categories?.ai || ''
  security.value = data.categories?.security || ''
}

async function update(category: string, value: string) {
  await fetch(`${apiBase}/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ category, value }),
  })
}

async function save() {
  await Promise.all([
    update('theme', theme.value),
    update('language', language.value),
    update('git', git.value),
    update('build', build.value),
    update('ai', ai.value),
    update('security', security.value),
  ])
}

onMounted(() => { void load() })
</script>
