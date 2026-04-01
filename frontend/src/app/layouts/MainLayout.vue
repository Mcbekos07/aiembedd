<template>
  <div class="main-layout">
    <header class="app-header">
      <h1>AIEmbedd IDE</h1>
      <nav>
        <RouterLink to="/">Старт</RouterLink>
        <RouterLink to="/ide">IDE</RouterLink>
        <RouterLink to="/build">Build</RouterLink>
        <RouterLink to="/devices">Устройства</RouterLink>
        <RouterLink to="/environment">Окружение</RouterLink>
        <RouterLink to="/git">Git</RouterLink>
        <RouterLink to="/versions">Версии</RouterLink>
        <RouterLink to="/history">История</RouterLink>
        <RouterLink to="/ai">AI</RouterLink>
        <RouterLink to="/prompts">Prompts</RouterLink>
        <RouterLink to="/settings">Настройки</RouterLink>
      </nav>
    </header>
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>
