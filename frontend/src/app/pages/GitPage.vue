<template>
  <section class="panel">
    <h2>Git</h2>
    <BranchSelector :project-id="projectId" />
    <GitStatusPanel :project-id="projectId" />
    <GitDiffPanel :project-id="projectId" />
    <CommitDialog :project-id="projectId" />
    <RemoteManager :project-id="projectId" />
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BranchSelector from '../components/git/BranchSelector.vue'
import CommitDialog from '../components/git/CommitDialog.vue'
import GitDiffPanel from '../components/git/GitDiffPanel.vue'
import GitStatusPanel from '../components/git/GitStatusPanel.vue'
import RemoteManager from '../components/git/RemoteManager.vue'

const route = useRoute()
const projectId = computed(() => Number(route.params.projectId || 0))
</script>
