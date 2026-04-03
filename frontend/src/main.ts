import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './app/router'
import './app/styles/base.css'
import './app/styles/theme-dark.css'
import './app/styles/layout.css'

createApp(App).use(createPinia()).use(router).mount('#app')
