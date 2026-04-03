<template>
  <div class="panel form">
    <h3>Remote</h3>
    <label>Имя <input v-model="name" /></label>
    <label>URL <input v-model="url" /></label>
    <div class="row">
      <Button @click="add">Добавить remote</Button>
      <Button @click="fetchRemote">Fetch</Button>
      <Button @click="pullRemote">Pull</Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from '../common/Button.vue'
import { useGitStore } from '../../store/gitStore'

const props = defineProps<{ projectId: number }>()
const store = useGitStore()
const name = ref('origin')
const url = ref('')

async function add() {
  await store.addRemote(props.projectId, name.value, url.value)
}

async function fetchRemote() {
  await store.fetchRemote(props.projectId)
}

async function pullRemote() {
  await store.pullRemote(props.projectId)
}
</script>
