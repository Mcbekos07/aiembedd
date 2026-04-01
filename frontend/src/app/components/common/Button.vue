<template>
  <button class="btn" :type="type">
    <slot />
  </button>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ type?: 'button' | 'submit' }>(), {
  type: 'button',
})
</script>
