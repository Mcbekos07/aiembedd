<template>
  <section class="panel">
    <h2>Окружение</h2>
    <DependencyPanel />
    <ToolchainPanel />
  </section>
</template>

<script setup lang="ts">
import DependencyPanel from '../components/environment/DependencyPanel.vue'
import ToolchainPanel from '../components/environment/ToolchainPanel.vue'
</script>
