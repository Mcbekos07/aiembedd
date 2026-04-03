<template>
  <span class="badge" :class="`badge-${tone}`">{{ label }}</span>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  tone?: 'ok' | 'warn' | 'info'
}>()
</script>
