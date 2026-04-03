import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import MainLayout from './layouts/MainLayout.vue'
import StartLayout from './layouts/StartLayout.vue'
import IdeLayout from './layouts/IdeLayout.vue'
import StartPage from './pages/StartPage.vue'
import NewProjectPage from './pages/NewProjectPage.vue'
import ImportProjectPage from './pages/ImportProjectPage.vue'
import CloneProjectPage from './pages/CloneProjectPage.vue'
import IdePage from './pages/IdePage.vue'
import SettingsPage from './pages/SettingsPage.vue'
import GitPage from './pages/GitPage.vue'
import VersionsPage from './pages/VersionsPage.vue'
import HistoryPage from './pages/HistoryPage.vue'
import BuildPage from './pages/BuildPage.vue'
import DevicesPage from './pages/DevicesPage.vue'
import EnvironmentPage from './pages/EnvironmentPage.vue'
import AiPage from './pages/AiPage.vue'
import PromptPage from './pages/PromptPage.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        component: StartLayout,
        children: [
          { path: '', name: 'start', component: StartPage },
          { path: 'new-project', name: 'new-project', component: NewProjectPage },
          { path: 'import-project', name: 'import-project', component: ImportProjectPage },
          { path: 'clone-project', name: 'clone-project', component: CloneProjectPage },
        ],
      },
      { path: 'ide/:projectId?', component: IdeLayout, children: [{ path: '', name: 'ide', component: IdePage }] },
      { path: 'git/:projectId?', name: 'git', component: GitPage },
      { path: 'versions/:projectId?', name: 'versions', component: VersionsPage },
      { path: 'history/:projectId?', name: 'history', component: HistoryPage },
      { path: 'build/:projectId?', name: 'build', component: BuildPage },
      { path: 'devices', name: 'devices', component: DevicesPage },
      { path: 'environment', name: 'environment', component: EnvironmentPage },
      { path: 'ai/:projectId?', name: 'ai', component: AiPage },
      { path: 'prompts/:projectId?', name: 'prompts', component: PromptPage },
      { path: 'settings', name: 'settings', component: SettingsPage },
    ],
  },
]

export default createRouter({ history: createWebHistory(), routes })
