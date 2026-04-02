<template>
  <div class="panel form">
    <h3>Создать версию</h3>
    <select v-model="kind">
      <option value="patch">patch</option>
      <option value="minor">minor</option>
      <option value="major">major</option>
    </select>
    <label><input v-model="withTag" type="checkbox" /> Создать Git tag</label>
    <Button @click="create">Создать</Button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Button from '../common/Button.vue'
import { useGitStore } from '../../store/gitStore'

const props = defineProps<{ projectId: number }>()
const store = useGitStore()
const kind = ref<'patch' | 'minor' | 'major'>('patch')
const withTag = ref(false)

async function create() {
  await store.createVersion(props.projectId, kind.value, withTag.value)
}
</script>
