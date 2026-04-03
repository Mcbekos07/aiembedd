<template>
  <section class="panel">
    <h2>Версии</h2>
    <VersionPanel :project-id="projectId" />
    <VersionCreateDialog :project-id="projectId" />
    <VersionHistoryList :project-id="projectId" />
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import VersionCreateDialog from '../components/git/VersionCreateDialog.vue'
import VersionHistoryList from '../components/git/VersionHistoryList.vue'
import VersionPanel from '../components/git/VersionPanel.vue'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId || 0))
</script>
