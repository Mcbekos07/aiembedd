<template>
  <aside class="panel ide-right">
    <h3>Project Intelligence</h3>
    <p>{{ intelligence?.summary || 'Нет snapshot' }}</p>
    <p><strong>Entry:</strong> {{ firstOrDash(intelligence?.entry_points) }}</p>
    <p><strong>Build files:</strong> {{ firstOrDash(intelligence?.known_build_paths) }}</p>

    <h4>Ключевые файлы</h4>
    <ul>
      <li v-for="file in (intelligence?.important_files || []).slice(0, 8)" :key="file">{{ file }}</li>
    </ul>

    <h4>Важные зависимости</h4>
    <ul>
      <li v-for="item in dependencyPreview" :key="item">{{ item }}</li>
    </ul>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { projectIntelligenceApi, type ProjectIntelligenceDto } from '../../services/projectIntelligenceApi'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId || 0))
const intelligence = ref<ProjectIntelligenceDto | null>(null)

const dependencyPreview = computed(() => {
  if (!intelligence.value) return []
  const pairs = Object.entries(intelligence.value.dependency_map)
  return pairs.slice(0, 6).map(([k, deps]) => `${k} -> ${deps.slice(0, 2).join(', ')}`)
})

const firstOrDash = (arr?: string[]) => (arr && arr.length > 0 ? arr[0] : '—')

watch(projectId, async (id) => {
  if (!id) return
  intelligence.value = await projectIntelligenceApi.get(id)
}, { immediate: true })
</script>
