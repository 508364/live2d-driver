import { createRouter, createWebHashHistory } from 'vue-router'
import Home from './Home.vue'
import Camera from './Camera.vue'
import Upload from './Upload.vue'
import Logs from './Logs.vue'
import About from './About.vue'
import Settings from './Settings.vue'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', component: Home, name: 'Home' },
  { path: '/camera', component: Camera, name: 'Camera' },
  { path: '/upload', component: Upload, name: 'Upload' },
  { path: '/logs', component: Logs, name: 'Logs' },
  { path: '/about', component: About, name: 'About' },
  { path: '/settings', component: Settings, name: 'Settings' }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router