<template>
  <div class="panel">
    <h3>Управление сборкой</h3>
    <p class="muted">Ручной контур сборки/прошивки всегда доступен и не блокируется агентом.</p>
    <p v-if="store.lastError" class="error">{{ store.lastError }}</p>
    <div class="grid-actions">
      <Button @click="store.prepare(projectId)" :disabled="busy">Подготовить</Button>
      <Button @click="store.build(projectId)" :disabled="busy">Собрать</Button>
      <Button @click="store.clean(projectId)" :disabled="busy">Очистить</Button>
      <Button @click="store.rebuild(projectId)" :disabled="busy">Пересобрать</Button>
      <Button @click="store.flash(projectId, programmer, port)" :disabled="busy">Прошить</Button>
    </div>
    <p v-if="busy" class="muted">Выполняется: {{ runningLabel }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Button from '../common/Button.vue'
import { useBuildStore } from '../../store/buildStore'

defineProps<{ projectId: number; programmer: string; port: string }>()
const store = useBuildStore()

const busy = computed(() => !!store.runningAction)
const runningLabel = computed(() => {
  const labels: Record<string, string> = {
    prepare: 'подготовка проекта',
    build: 'сборка проекта',
    clean: 'очистка артефактов',
    rebuild: 'полная пересборка',
    flash: 'прошивка устройства',
  }
  return labels[store.runningAction] || 'операция'
})
</script>
