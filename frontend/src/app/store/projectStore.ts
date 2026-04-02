import { defineStore } from 'pinia'
import { fileApi } from '../services/fileApi'
import { projectApi, type CloneProjectPayload, type CreateProjectPayload, type ImportProjectPayload, type ProjectDto } from '../services/projectApi'

interface ProjectState {
  projects: ProjectDto[]
  loading: boolean
  error: string
  fileTree: Array<{ path: string; type: string }>
  openedFilePath: string
  openedFileContent: string
}

export const useProjectStore = defineStore('project', {
  state: (): ProjectState => ({
    projects: [],
    loading: false,
    error: '',
    fileTree: [],
    openedFilePath: '',
    openedFileContent: '',
  }),
  actions: {
    async fetchProjects(): Promise<void> {
      this.loading = true
      this.error = ''
      try {
        this.projects = await projectApi.list()
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Не удалось получить проекты'
      } finally {
        this.loading = false
      }
    },

    async createProject(payload: CreateProjectPayload): Promise<void> {
      const project = await projectApi.create(payload)
      this.projects.unshift(project)
    },

    async importLocalProject(payload: ImportProjectPayload): Promise<void> {
      const project = await projectApi.importLocal(payload)
      this.projects.unshift(project)
    },

    async cloneProject(payload: CloneProjectPayload): Promise<void> {
      await projectApi.cloneRemote(payload)
      await this.fetchProjects()
    },

    async deleteProject(projectId: number, mode: 'registry_only' | 'registry_with_history' | 'full', confirmed: boolean): Promise<void> {
      await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/projects/${projectId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode, confirmed }),
      })
      this.projects = this.projects.filter((item) => item.id !== projectId)
    },

    async loadTree(projectId: number): Promise<void> {
      this.fileTree = (await fileApi.tree(projectId)).items
    },

    async openFile(projectId: number, path: string): Promise<void> {
      this.openedFilePath = path
      this.openedFileContent = (await fileApi.read(projectId, path)).content
    },

    async saveFile(projectId: number): Promise<void> {
      if (!this.openedFilePath) return
      await fileApi.save(projectId, this.openedFilePath, this.openedFileContent)
      await this.loadTree(projectId)
    },

    async createEntry(projectId: number, path: string, kind: 'file' | 'folder'): Promise<void> {
      await fileApi.create(projectId, path, kind)
      await this.loadTree(projectId)
    },
  },
})
