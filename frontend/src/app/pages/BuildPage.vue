<template>
  <section class="panel">
    <h2>Сборка и прошивка</h2>
    <p class="muted">Ручные действия по сборке/прошивке доступны параллельно с агентными сценариями.</p>
    <BuildProfileSelector />
    <ProgrammerSelector v-model:programmer="programmer" />
    <PortSelector v-model:port="port" />
    <BuildControlPanel :project-id="projectId" :programmer="programmer" :port="port" />
    <BuildStatusPanel />
    <BuildHistoryList />
    <RuntimeObservePanel :project-id="projectId" />
    <ArtifactList />
    <LogToolbar />
    <ErrorSummaryPanel />
    <LogConsole />
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import ArtifactList from '../components/build/ArtifactList.vue'
import BuildControlPanel from '../components/build/BuildControlPanel.vue'
import BuildHistoryList from '../components/build/BuildHistoryList.vue'
import BuildProfileSelector from '../components/build/BuildProfileSelector.vue'
import BuildStatusPanel from '../components/build/BuildStatusPanel.vue'
import RuntimeObservePanel from '../components/build/RuntimeObservePanel.vue'
import PortSelector from '../components/devices/PortSelector.vue'
import ProgrammerSelector from '../components/devices/ProgrammerSelector.vue'
import ErrorSummaryPanel from '../components/logs/ErrorSummaryPanel.vue'
import LogConsole from '../components/logs/LogConsole.vue'
import LogToolbar from '../components/logs/LogToolbar.vue'
import { useBuildStore } from '../store/buildStore'
import { useRealtimeStore } from '../store/realtimeStore'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId || 0))
const programmer = ref('stlink')
const port = ref('/dev/ttyUSB0')
const buildStore = useBuildStore()
const realtimeStore = useRealtimeStore()

watch(projectId, (id) => {
  if (id > 0) {
    void buildStore.fetchHistory(id)
    void buildStore.refreshRuntime(id)
    realtimeStore.connect(id)
  }
}, { immediate: true })

onBeforeUnmount(() => {
  realtimeStore.disconnect()
})
</script>
