<template>
  <div id="app" :class="themeClass">
    <!-- 应用布局 -->
    <div class="app-container">
      <!-- 侧边导航栏 -->
      <div class="sidebar">
        <div class="app-header">
          <div class="app-logo">Live2D驱动器 Beta</div>
        </div>
        
        <div class="nav-items">
          <div 
            v-for="item in navItems" 
            :key="item.name" 
            class="nav-item"
            :class="{ active: activeNav === item.name }"
            @click="activeNav = item.name"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-text">{{ item.text }}</span>
          </div>
        </div>
      </div>
      
      <!-- 主内容区 -->
      <div class="main-content">
        <div class="content-header">
          <h2>{{ activeNav }}</h2>
        </div>
        
        <div class="content-body">
          <component :is="activeComponent" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Home from './Home.vue'
import Camera from './Camera.vue'
import Upload from './Upload.vue'
import Logs from './Logs.vue'
import About from './About.vue'
import Settings from './Settings.vue'
import { useThemeStore } from './stores/theme'

const navComponents = {
  '首页': Home,
  '虚拟摄像头': Camera,
  '上传live2d形象': Upload,
  '日志': Logs,
  '关于': About,
  '设置': Settings
}

export default {
  data() {
    return {
      navItems: [
        { name: '首页', text: '首页', icon: '🏠' },
        { name: '虚拟摄像头', text: '虚拟摄像头', icon: '📷' },
        { name: '上传live2d形象', text: '上传live2d形象', icon: '📁' },
        { name: '日志', text: '日志', icon: '📝' },
        { name: '关于', text: '关于', icon: 'ℹ️' },
        { name: '设置', text: '设置', icon: '⚙️' }
      ],
      activeNav: '首页'
    }
  },
  
  computed: {
    activeComponent() {
      return navComponents[this.activeNav]
    },
    themeClass() {
      const themeStore = useThemeStore()
      return `${themeStore.currentTheme}-theme`
    }
  }
}
</script>

<style>
/* 全局样式 */
:root {
  --primary-color: #42b983;
  --background: #1e1e1e;
  --text-color: #ffffff;
  --card-bg: #2d2d2d;
  --sidebar-bg: #252525;
}

.dark-theme {
  --primary-color: #42b983;
  --background: #1e1e1e;
  --text-color: #ffffff;
  --card-bg: #2d2d2d;
  --sidebar-bg: #252525;
}

.light-theme {
  --primary-color: #42b983;
  --background: #ffffff;
  --text-color: #333333;
  --card-bg: #f5f5f5;
  --sidebar-bg: #e0e0e0;
}

.blue-theme {
  --primary-color: #2196f3;
  --background: #0d47a1;
  --text-color: #ffffff;
  --card-bg: #283593;
  --sidebar-bg: #1a237e;
}

#app {
  height: 100vh;
  background-color: var(--background);
  color: var(--text-color);
  font-family: 'Arial', sans-serif;
  overflow: hidden;
}

.app-container {
  display: flex;
  height: 100%;
}

.sidebar {
  width: 240px;
  background-color: var(--sidebar-bg);
  padding: 20px;
  box-sizing: border-box;
  box-shadow: 2px 0 5px rgba(0,0,0,0.1);
}

.app-header {
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.app-logo {
  font-size: 18px;
  font-weight: bold;
  color: var(--primary-color);
}

.nav-items {
  margin-top: 30px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.nav-item:hover {
  background: rgba(255,255,255,0.1);
}

.nav-item.active {
  background: var(--primary-color);
  color: #fff;
}

.nav-icon {
  margin-right: 15px;
  font-size: 18px;
}

.nav-text {
  font-size: 16px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
}

.content-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.content-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.content-body {
  flex: 1;
  padding: 10px;
}
</style>