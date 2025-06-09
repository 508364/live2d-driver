import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import router from './router'

// 模拟Live2D加载 - 实际项目应使用SDK
window.Live2DCubismCore = {
  core: {
    init: () => console.log('Live2D Core initialized'),
    createModel: async (path) => {
      console.log('Loading Live2D model:', path)
      return {
        setParam: (param, value) => console.log(`Set ${param} to ${value}`),
        update: () => {},
        draw: () => {}
      }
    }
  }
}

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')

console.log('Vue app mounted')