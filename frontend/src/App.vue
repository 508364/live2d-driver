<template>
  <div id="app" :class="themeClass">
    <!-- 全局加载状态 -->
    <div v-if="showGlobalLoader" class="global-loader">
      <div class="loader-spinner"></div>
      <div class="loader-text">{{ globalLoaderText }}</div>
    </div>
    
    <!-- 应用内容 -->
    <div class="app-container">
      <!-- 侧边导航栏 -->
      <div class="sidebar">
        <div class="app-header">
          <div class="app-logo">
            <div class="app-icon">👤</div>
            <div class="app-title">Live2D驱动器</div>
            <div class="app-version">v1.0.0</div>
          </div>
        </div>
        
        <div class="nav-items">
          <div 
            v-for="item in navItems" 
            :key="item.name" 
            class="nav-item"
            :class="{ active: activeNav === item.name }"
            @click="setActiveNav(item.name)"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-text">{{ item.text }}</span>
          </div>
        </div>
        
        <div class="sidebar-footer">
          <div class="fps-counter" v-if="fps > 0">
            <span class="fps-icon">📊</span>
            <span class="fps-value">{{ fps }} FPS</span>
          </div>
          
          <div class="status-indicator">
            <div class="indicator-dot" :class="statusColor"></div>
            <span class="status-text">{{ appStatus }}</span>
          </div>
        </div>
      </div>
      
      <!-- 主内容区 -->
      <div class="main-content">
        <div class="content-header">
          <h2>{{ activeNav }}</h2>
          <div class="header-actions">
            <button 
              v-if="activeNav === '首页'" 
              class="track-btn" 
              :class="{ active: isTracking }"
              @click="toggleTracking"
            >
              <span class="track-icon">{{ isTracking ? '⏹️' : '▶️' }}</span>
              <span class="track-text">{{ isTracking ? '停止追踪' : '开始追踪' }}</span>
            </button>
            <button class="refresh-btn" @click="reloadPage">🔄</button>
          </div>
        </div>
        
        <div class="content-body">
          <Home v-if="activeNav === '首页'" ref="homeComponent" />
          <Camera v-if="activeNav === '虚拟摄像头'" />
          <Upload v-if="activeNav === '上传live2d形象'" />
          <Logs v-if="activeNav === '日志'" />
          <About v-if="activeNav === '关于'" />
          <Settings v-if="activeNav === '设置'" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Home from './components/Home.vue'
import Camera from './components/Camera.vue'
import Upload from './components/Upload.vue'
import Logs from './components/Logs.vue'
import About from './components/About.vue'
import Settings from './components/Settings.vue'
import { useThemeStore } from './stores/theme'
import { useLogStore } from './stores/logs'
import { useTrackingStore } from './stores/tracking'

export default {
  components: { Home, Camera, Upload, Logs, About, Settings },
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
      activeNav: '首页',
      showGlobalLoader: true,
      globalLoaderText: '正在加载应用资源...',
      appStatus: '就绪',
      fps: 0,
      fpsCounter: 0,
      lastFpsUpdate: 0,
      isTracking: false
    }
  },
  computed: {
    themeClass() {
      const themeStore = useThemeStore()
      return `${themeStore.currentTheme}-theme`
    },
    statusColor() {
      if (this.isTracking) return 'green'
      return 'gray'
    }
  },
  created() {
    // 应用加载完成后隐藏全局加载器
    setTimeout(() => {
      this.showGlobalLoader = false
    }, 2500)
    
    // 设置主题
    const themeStore = useThemeStore()
    themeStore.applyTheme()
    
    // 初始化日志
    const logStore = useLogStore()
    logStore.addLog('应用初始化')
  },
  mounted() {
    // FPS计数
    this.startFpsCounter()
    
    // 监听页面刷新按钮
    window.addEventListener('beforeunload', () => {
      const trackingStore = useTrackingStore()
      if (trackingStore.isRunning) {
        trackingStore.stopTracking()
      }
    })
  },
  methods: {
    setActiveNav(navName) {
      this.activeNav = navName
      const logStore = useLogStore()
      logStore.addLog(`导航到: ${navName}`)
    },
    
    toggleTracking() {
      this.isTracking = !this.isTracking
      const trackingStore = useTrackingStore()
      
      if (this.isTracking) {
        this.appStatus = '追踪中...'
        trackingStore.startTracking()
        logStore.addLog('开始面部追踪')
      } else {
        this.appStatus = '就绪'
        trackingStore.stopTracking()
        logStore.addLog('停止面部追踪')
      }
    },
    
    reloadPage() {
      window.location.reload()
    },
    
    startFpsCounter() {
      requestAnimationFrame(this.updateFps)
    },
    
    updateFps(now) {
      this.fpsCounter++
      
      if (now - this.lastFpsUpdate > 1000) {
        this.fps = this.fpsCounter
        this.fpsCounter = 0
        this.lastFpsUpdate = now
      }
      
      requestAnimationFrame(this.updateFps)
    }
  }
}
</script>

<style>
#app {
  height: 100vh;
  display: flex;
  background-color: var(--background);
  color: var(--text-color);
  overflow: hidden;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 全局加载器 */
.global-loader {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: rgba(30, 30, 30, 0.95);
  z-index: 10000;
  color: #42b983;
}

.loader-spinner {
  border: 8px solid rgba(66, 185, 131, 0.3);
  border-top: 8px solid #42b983;
  border-radius: 50%;
  width: 80px;
  height: 80px;
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loader-text {
  margin-top: 30px;
  font-size: 20px;
  font-weight: 500;
}

/* 应用容器 */
.app-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 260px;
  background: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  padding: 20px 0;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 10;
}

.app-header {
  padding: 0 20px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 20px;
}

.app-logo {
  display: flex;
  align-items: center;
}

.app-icon {
  font-size: 32px;
  margin-right: 10px;
}

.app-title {
  font-size: 20px;
  font-weight: bold;
  color: var(--primary-color);
}

.app-version {
  font-size: 12px;
  color: #aaa;
  margin-top: 2px;
}

.nav-items {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  margin-bottom: 6px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  color: var(--text-secondary);
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  background: var(--primary-color);
  color: white;
}

.nav-icon {
  margin-right: 15px;
  font-size: 20px;
  width: 24px;
  text-align: center;
}

.nav-text {
  font-size: 16px;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.fps-counter {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.fps-icon {
  margin-right: 10px;
  font-size: 18px;
}

.fps-value {
  font-size: 14px;
  color: #42b983;
  font-family: monospace;
}

.status-indicator {
  display: flex;
  align-items: center;
  margin-top: 15px;
}

.indicator-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 10px;
}

.indicator-dot.green {
  background-color: #42b983;
  box-shadow: 0 0 10px rgba(66, 185, 131, 0.5);
}

.indicator-dot.gray {
  background-color: #888;
}

.status-text {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.content-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--primary-color);
}

.header-actions {
  display: flex;
  gap: 10px;
}

.track-btn {
  display: flex;
  align-items: center;
  background: rgba(66, 185, 131, 0.15);
  color: #42b983;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
}

.track-btn.active {
  background: rgba(255, 99, 99, 0.15);
  color: #ff6363;
}

.track-btn:hover {
  background: rgba(66, 185, 131, 0.25);
}

.track-btn.active:hover {
  background: rgba(255, 99, 99, 0.25);
}

.track-icon {
  margin-right: 8px;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(180deg);
}

/* 内容主体 */
.content-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* 主题变量 */
.dark-theme {
  --primary-color: #42b983;
  --background: #1e1e1e;
  --sidebar-bg: #252525;
  --text-primary: #ffffff;
  --text-secondary: #cccccc;
  --card-bg: #2d2d2d;
}

.light-theme {
  --primary-color: #42b983;
  --background: #f9f9f9;
  --sidebar-bg: #f5f5f5;
  --text-primary: #333333;
  --text-secondary: #666666;
  --card-bg: #ffffff;
}

.blue-theme {
  --primary-color: #2196f3;
  --background: #0d47a1;
  --sidebar-bg: #1a237e;
  --text-primary: #ffffff;
  --text-secondary: #cccccc;
  --card-bg: #283593;
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: var(--primary-color);
  border-radius: 4px;
}
</style>