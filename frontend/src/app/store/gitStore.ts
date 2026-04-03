import { defineStore } from 'pinia'
import { gitApi, type VersionRow, type AgentCheckpoint } from '../services/gitApi'

export const useGitStore = defineStore('git', {
  state: () => ({
    branches: [] as string[],
    currentBranch: '',
    diffOutput: '',
    versions: [] as VersionRow[],
    currentVersion: '0.1.0',
    checkpoints: [] as AgentCheckpoint[],
    suggestedCommitMessage: '',
  }),
  actions: {
    async fetchBranches(projectId: number): Promise<void> {
      const data = await gitApi.branches(projectId)
      this.branches = data.branches
      this.currentBranch = data.current_branch
    },
    async switchBranch(projectId: number, branch: string): Promise<void> {
      await gitApi.switchBranch(projectId, branch)
      this.currentBranch = branch
    },
    async fetchDiff(projectId: number): Promise<void> {
      const data = await gitApi.diff(projectId)
      this.diffOutput = data.output
    },
    async commit(projectId: number, message: string): Promise<void> {
      await gitApi.commit(projectId, message)
    },
    async fetchRemote(projectId: number): Promise<void> {
      await gitApi.fetchRemote(projectId)
    },
    async pullRemote(projectId: number): Promise<void> {
      await gitApi.pullRemote(projectId)
    },
    async addRemote(projectId: number, name: string, url: string): Promise<void> {
      await gitApi.addRemote(projectId, name, url)
    },
    async fetchVersions(projectId: number): Promise<void> {
      const data = await gitApi.versions(projectId)
      this.versions = data.items
      if (this.versions.length > 0) {
        this.currentVersion = this.versions[0].version
      }
    },
    async createVersion(projectId: number, kind: string, withTag: boolean): Promise<void> {
      await gitApi.createVersion(projectId, kind, withTag)
      await this.fetchVersions(projectId)
    },
    async fetchCheckpoints(projectId: number): Promise<void> {
      const data = await gitApi.listCheckpoints(projectId)
      this.checkpoints = data.items
    },
    async createCheckpoint(projectId: number, checkpointType: string, message: string, taskId = 0, note = ''): Promise<void> {
      await gitApi.createCheckpoint(projectId, checkpointType, message, taskId, note)
      await this.fetchCheckpoints(projectId)
    },
    async restoreCheckpoint(projectId: number, checkpointId: number): Promise<void> {
      await gitApi.restoreCheckpoint(projectId, checkpointId)
      await this.fetchCheckpoints(projectId)
    },
    async suggestCommitMessage(projectId: number, taskId: number): Promise<void> {
      const data = await gitApi.suggestCommitMessage(projectId, taskId)
      this.suggestedCommitMessage = data.message
    },
    async createVersionFromTask(projectId: number, taskId: number, kind: string, note: string, withTag: boolean): Promise<void> {
      await gitApi.createVersionFromTask(projectId, taskId, kind, note, withTag)
      await this.fetchVersions(projectId)
    },
  },
})
