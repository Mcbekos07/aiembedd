<template>
  <section class="panel">
    <h2>Build & Flash</h2>
    <BuildProfileSelector />
    <ProgrammerSelector v-model:programmer="programmer" />
    <PortSelector v-model:port="port" />
    <BuildControlPanel :project-id="projectId" :programmer="programmer" :port="port" />
    <BuildStatusPanel />
    <BuildHistoryList />
    <ArtifactList />
    <LogToolbar />
    <ErrorSummaryPanel />
    <LogConsole />
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import ArtifactList from '../components/build/ArtifactList.vue'
import BuildControlPanel from '../components/build/BuildControlPanel.vue'
import BuildHistoryList from '../components/build/BuildHistoryList.vue'
import BuildProfileSelector from '../components/build/BuildProfileSelector.vue'
import BuildStatusPanel from '../components/build/BuildStatusPanel.vue'
import PortSelector from '../components/devices/PortSelector.vue'
import ProgrammerSelector from '../components/devices/ProgrammerSelector.vue'
import ErrorSummaryPanel from '../components/logs/ErrorSummaryPanel.vue'
import LogConsole from '../components/logs/LogConsole.vue'
import LogToolbar from '../components/logs/LogToolbar.vue'
import { useBuildStore } from '../store/buildStore'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId || 0))
const programmer = ref('stlink')
const port = ref('/dev/ttyUSB0')
useBuildStore().fetchHistory(projectId.value)
</script>
