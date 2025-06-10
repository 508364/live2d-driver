<!-- frontend/src/App.vue -->
<template>
  <div id="app" :class="themeClass">
    <!-- 全局加载状态 -->
    <div v-if="showGlobalLoader" class="global-loader">
      <div class="loader-spinner"></div>
      <div class="loader-text">{{ globalLoaderText }}</div>
    </div>
    
    <!-- 应用主界面 -->
    <div v-show="!showGlobalLoader" class="app-container">
      <!-- 侧边栏 -->
      <div class="sidebar">
        <div class="app-header">
          <div class="app-logo">Live2D Drive</div>
          <div class="app-version">v1.0.0</div>
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
        
        <div class="status-panel">
          <div class="status-row">
            <span class="status-label">摄像头:</span>
            <span :class="cameraStatusClass">{{ cameraStatus }}</span>
          </div>
          <div class="status-row">
            <span class="status-label">追踪:</span>
            <span :class="trackingStatusClass">{{ trackingStatus }}</span>
          </div>
          <div class="status-row">
            <span class="status-label">FPS:</span>
            <span>{{ fps }}</span>
          </div>
        </div>
      </div>
      
      <!-- 主内容区 -->
      <div class="main-content">
        <div class="content-header">
          <h2>{{ activeNav }}</h2>
          <div class="header-actions">
            <button v-if="activeNav === '首页'" class="action-btn" @click="toggleTracking">
              <span>{{ trackingActive ? '⏹️ 停止' : '▶️ 开始' }}追踪</span>
            </button>
            <button class="action-btn" @click="refreshApp">
              <span>🔄 刷新</span>
            </button>
          </div>
        </div>
        
        <div class="content-body">
          <Home v-if="activeNav === '首页'" ref="homeComponent" />
          <Camera v-if="activeNav === '虚拟摄像头'" />
          <Upload v-if="activeNav === '上传模型'" />
          <Logs v-if="activeNav === '日志'" />
          <Settings v-if="activeNav === '设置'" />
        </div>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="showConnectionError" class="connection-error">
      <div class="error-content">
        <h3>⚠️ 连接失败</h3>
        <p>无法连接到前端开发服务器</p>
        <p>请检查：</p>
        <ul>
          <li>终端中是否有错误消息</li>
          <li>端口3000是否被其他应用占用</li>
          <li>防火墙设置是否允许访问</li>
        </ul>
        <div class="action-buttons">
          <button @click="retryConnection">⟳ 重试</button>
          <button @click="openDevTools">🐞 打开开发者工具</button>
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
import Settings from './components/Settings.vue'
import { useAppStore } from './stores/app'
import { useTrackingStore } from './stores/tracking'

export default {
  components: { Home, Camera, Upload, Logs, Settings },
  data() {
    return {
      showGlobalLoader: true,
      globalLoaderText: '初始化应用程序...',
      showConnectionError: false,
      activeNav: '首页',
      trackingActive: false,
      navItems: [
        { name: 'home', text: '首页', icon: '🏠' },
        { name: 'camera', text: '虚拟摄像头', icon: '📷' },
        { name: 'upload', text: '上传模型', icon: '📁' },
        { name: 'logs', text: '运行日志', icon: '📝' },
        { name: 'settings', text: '系统设置', icon: '⚙️' }
      ],
      fps: 0,
      fpsCounter: 0,
      lastFpsTime: 0,
      connectionCheckInterval: null,
      cameraStatus: '未连接',
      trackingStatus: '未启动'
    }
  },
  computed: {
    themeClass() {
      const appStore = useAppStore()
      return `theme-${appStore.theme}`
    },
    cameraStatusClass() {
      return this.cameraStatus === '已连接' ? 'status-on' : 'status-off'
    },
    trackingStatusClass() {
      return this.trackingActive ? 'status-on' : 'status-off'
    }
  },
  mounted() {
    // 模拟加载过程
    setTimeout(() => {
      this.globalLoaderText = '加载核心模块...'
    }, 1000)
    
    setTimeout(() => {
      this.globalLoaderText = '初始化AI模型...'
    }, 2000)
    
    setTimeout(() => {
      this.globalLoaderText = '准备用户界面...'
    }, 3000)
    
    // 完成加载
    setTimeout(() => {
      this.showGlobalLoader = false
      this.initApp()
    }, 4000)
    
    // 检查服务器连接
    this.connectionCheckInterval = setInterval(() => {
      this.checkServerConnection()
    }, 5000)
  },
  beforeUnmount() {
    clearInterval(this.connectionCheckInterval)
  },
  methods: {
    initApp() {
      // 启动FPS计数
      this.startFpsCounter()
      
      // 检查后端连接
      this.checkServerConnection()
    },
    
    startFpsCounter() {
      const updateFps = (now) => {
        this.fpsCounter++
        if (now - this.lastFpsTime >= 1000) {
          this.fps = this.fpsCounter
          this.fpsCounter = 0
          this.lastFpsTime = now
        }
        requestAnimationFrame(updateFps)
      }
      requestAnimationFrame(updateFps)
    },
    
    checkServerConnection() {
      fetch('http://localhost:3000')
        .then(response => {
          if (response.status === 200) {
            this.showConnectionError = false
            this.cameraStatus = '已连接'
          }
        })
        .catch(() => {
          this.showConnectionError = true
          this.cameraStatus = '连接失败'
        })
    },
    
    setActiveNav(nav) {
      this.activeNav = nav
    },
    
    toggleTracking() {
      this.trackingActive = !this.trackingActive
      this.trackingStatus = this.trackingActive ? '运行中' : '已停止'
      
      // 更新追踪状态
      const trackingStore = useTrackingStore()
      if (this.trackingActive) {
        trackingStore.startTracking()
        this.$refs.homeComponent?.startFaceTracking()
      } else {
        trackingStore.stopTracking()
        this.$refs.homeComponent?.stopFaceTracking()
      }
    },
    
    refreshApp() {
      window.location.reload()
    },
    
    retryConnection() {
      this.showConnectionError = false
      this.checkServerConnection()
    },
    
    openDevTools() {
      try {
        // 尝试用键盘事件打开开发者工具
        const event = new KeyboardEvent('keydown', {
          key: 'F12',
          code: 'F12',
          keyCode: 123,
          which: 123,
          ctrlKey: true,
          shiftKey: true
        })
        document.dispatchEvent(event)
      } catch (e) {
        alert('无法打开开发者工具，请手动按F12键')
      }
    }
  }
}
</script>

<style scoped>
#app {
  height: 100vh;
  display: flex;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow: hidden;
  background-color: #1e1e1e;
  color: #f0f0f0;
}

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
  z-index: 1000;
}

.loader-spinner {
  border: 6px solid rgba(66, 185, 131, 0.3);
  border-top: 6px solid #42b983;
  border-radius: 50%;
  width: 80px;
  height: 80px;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loader-text {
  font-size: 18px;
  color: #42b983;
}

.app-container {
  display: flex;
  width: 100%;
  height: 100%;
}

.sidebar {
  width: 260px;
  background: #252525;
  display: flex;
  flex-direction: column;
  padding: 20px 0;
  border-right: 1px solid #333;
}

.app-header {
  padding: 0 20px 20px;
  border-bottom: 1px solid #333;
  margin-bottom: 15px;
}

.app-logo {
  font-size: 22px;
  font-weight: bold;
  color: #42b983;
  margin-bottom: 5px;
}

.app-version {
  font-size: 12px;
  color: #888;
}

.nav-items {
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  margin: 5px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  background: #42b983;
  color: white;
}

.nav-icon {
  margin-right: 12px;
  font-size: 20px;
}

.nav-text {
  font-size: 16px;
}

.status-panel {
  padding: 15px;
  background: rgba(0, 0, 0, 0.2);
  margin: 15px;
  border-radius: 8px;
}

.status-row {
  display: flex;
  justify-content: space-between;
  margin: 8px 0;
  font-size: 14px;
}

.status-label {
  color: #aaa;
}

.status-on {
  color: #42b983;
  font-weight: 500;
}

.status-off {
  color: #ff6b6b;
  font-weight: 500;
}

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
  padding: 15px 20px;
  border-bottom: 1px solid #333;
  background: rgba(0, 0, 0, 0.2);
}

.content-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
  color: #f0f0f0;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.content-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.connection-error {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.error-content {
  background: #2d2d2d;
  border: 1px solid #ff6b6b;
  border-radius: 10px;
  padding: 30px;
  max-width: 600px;
  width: 90%;
  text-align: center;
}

.error-content h3 {
  color: #ff6b6b;
  margin-top: 0;
}

.error-content p {
  margin: 10px 0;
}

.error-content ul {
  text-align: left;
  max-width: 80%;
  margin: 15px auto;
  padding-left: 20px;
}

.error-content li {
  margin: 8px 0;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 25px;
}

.action-buttons button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
}

.action-buttons button:first-child {
  background: #42b983;
  color: white;
}

.action-buttons button:last-child {
  background: #2196f3;
  color: white;
}

/* 主题样式 */
.theme-dark {
  --primary-color: #42b983;
  --background: #1e1e1e;
  --card-bg: #2d2d2d;
  --text-color: #f0f0f0;
  --border-color: #444;
}

.theme-light {
  --primary-color: #42b983;
  --background: #f9f9f9;
  --card-bg: #ffffff;
  --text-color: #333;
  --border-color: #ddd;
}

.theme-blue {
  --primary-color: #2196f3;
  --background: #0d47a1;
  --card-bg: #1a237e;
  --text-color: #fff;
  --border-color: #283593;
}

body.theme-dark {
  background-color: var(--background);
  color: var(--text-color);
}

body.theme-light {
  background-color: var(--background);
  color: var(--text-color);
}

body.theme-blue {
  background-color: var(--background);
  color: var(--text-color);
}
</style>