// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',  // 允许外部访问
    port: 3000,
    strictPort: true, // 如果端口被占用则报错
    open: false       // 禁止Vite自动打开浏览器
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    minify: 'terser',
    sourcemap: true
  },
  preview: {
    port: 4173
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/assets/styles/variables.scss";`
      }
    }
  },
  optimizeDeps: {
    include: ['@tensorflow/tfjs', '@tensorflow-models/blazeface']
  }
})