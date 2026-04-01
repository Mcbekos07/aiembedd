<template>
  <div>
    <div class="row between">
      <h4>Файлы проекта</h4>
      <button class="btn" @click="createFile">+ Файл</button>
    </div>
    <ul class="list">
      <li v-for="item in store.fileTree" :key="item.path">
        <button class="btn" @click="open(item.path)">{{ item.path }}</button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { useProjectStore } from '../../store/projectStore'

const props = defineProps<{ projectId: number }>()
const store = useProjectStore()

function open(path: string) {
  void store.openFile(props.projectId, path)
}

function createFile() {
  const name = window.prompt('Имя файла', 'src/new_file.c')
  if (!name) return
  void store.createEntry(props.projectId, name, 'file')
}
</script>
