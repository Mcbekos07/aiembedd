<template>
  <div class="panel form">
    <h3>Память проекта V2</h3>
    <div class="row">
      <select v-model="memoryType">
        <option value="architecture_decision">architecture decision</option>
        <option value="known_risky_file">known risky file</option>
        <option value="known_good_fix">known good fix</option>
        <option value="repeated_failure_pattern">repeated failure pattern</option>
        <option value="hardware_runtime_note">hardware/runtime note</option>
        <option value="build_caveat">build caveat</option>
        <option value="flash_caveat">flash caveat</option>
        <option value="project_invariant">project invariant</option>
      </select>
      <input v-model="titleText" placeholder="title" />
    </div>
    <div class="row">
      <input v-model="valText" placeholder="content" />
      <input v-model.number="importance" type="number" min="1" max="5" placeholder="importance" />
    </div>
    <div class="row">
      <Button @click="addTyped">Добавить typed memory</Button>
      <Button @click="maintenance">Memory maintenance</Button>
    </div>

    <h4>Important project knowledge</h4>
    <ul class="list">
      <li v-for="(count, type) in store.memoryCounts" :key="type">{{ type }}: {{ count }}</li>
    </ul>

    <h4>Saved decisions / issues / fixes</h4>
    <ul class="list"><li v-for="m in store.memory" :key="m.created_at + m.key">[{{ m.memory_type }}] {{ m.title }}: {{ m.content }}</li></ul>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from '../common/Button.vue'
import { useAiStore } from '../../store/aiStore'

const props = defineProps<{ projectId: number }>()
const store = useAiStore()
const memoryType = ref('architecture_decision')
const titleText = ref('')
const valText = ref('')
const importance = ref(3)

async function addTyped() {
  await store.addTypedMemory(props.projectId, memoryType.value, titleText.value, valText.value, importance.value)
}

async function maintenance() {
  await store.runMemoryMaintenance(props.projectId)
}
</script>
