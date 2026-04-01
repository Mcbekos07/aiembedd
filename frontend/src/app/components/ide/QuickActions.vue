<template>
  <div class="panel">
    <h3>Быстрые действия</h3>
    <div class="grid-actions">
      <Button @click="store.saveFile(projectId)">Сохранить файл</Button>
      <Button>Создать версию</Button>
      <Button>Подготовить</Button>
      <Button>Собрать</Button>
      <Button>Прошить</Button>
      <Button>ИИ</Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import Button from '../common/Button.vue'
import { useProjectStore } from '../../store/projectStore'

const props = defineProps<{ projectId: number }>()
const store = useProjectStore()
const projectId = props.projectId
</script>
