<template>
  <div class="panel">
    <div class="row between">
      <h3>История версий</h3>
      <Button @click="load">Обновить</Button>
    </div>
    <ul class="list">
      <li v-for="row in store.versions" :key="row.version + row.created_at">
        {{ row.version }} ({{ row.kind }}) {{ row.tag_name ? `— ${row.tag_name}` : '' }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import Button from '../common/Button.vue'
import { useGitStore } from '../../store/gitStore'

const props = defineProps<{ projectId: number }>()
const store = useGitStore()

async function load() {
  await store.fetchVersions(props.projectId)
}
</script>
