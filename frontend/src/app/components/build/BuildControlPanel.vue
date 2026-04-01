<template>
  <div class="panel">
    <h3>Управление сборкой</h3>
    <div class="grid-actions">
      <Button @click="store.prepare(projectId)">Prepare</Button>
      <Button @click="store.build(projectId)">Build</Button>
      <Button @click="store.clean(projectId)">Clean</Button>
      <Button @click="store.rebuild(projectId)">Rebuild</Button>
      <Button @click="store.flash(projectId, programmer, port)">Flash</Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import Button from '../common/Button.vue'
import { useBuildStore } from '../../store/buildStore'

defineProps<{ projectId: number; programmer: string; port: string }>()
const store = useBuildStore()
</script>
