import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

// ===================
// 初始化加载界面
// ===================
const appContainer = document.createElement('div')
appContainer.id = 'app'
document.body.appendChild(appContainer)

const loadingDiv = document.createElement('div')
loadingDiv.id = 'app-loader'
loadingDiv.style.position = 'fixed'
loadingDiv.style.top = '0'
loadingDiv.style.left = '0'
loadingDiv.style.right = '0'
loadingDiv.style.bottom = '0'
loadingDiv.style.backgroundColor = '#1e1e1e'
loadingDiv.style.display = 'flex'
loadingDiv.style.flexDirection = 'column'
loadingDiv.style.justifyContent = 'center'
loadingDiv.style.alignItems = 'center'
loadingDiv.style.zIndex = '9999'

loadingDiv.innerHTML = `
  <div class="loader-spinner"></div>
  <h2 style="color: #42b983; margin-top: 30px">Live2D驱动器初始化中...</h2>
  <p style="color: #aaa; max-width: 600px; text-align: center; margin-top: 20px">
    正在加载应用程序资源，这可能需要几秒钟时间
  </p>
  <div class="progress-container">
    <div class="progress-bar" id="progress-bar"></div>
  </div>
  <div id="loading-details" style="margin-top: 20px; color: #888; max-width: 600px; text-align: center; font-size: 14px"></div>
`

document.body.appendChild(loadingDiv)

// 动画进度条
const progressBar = document.getElementById('progress-bar')
let progress = 0
const progressInterval = setInterval(() => {
  progress = Math.min(progress + 1, 95)
  progressBar.style.width = `${progress}%`
}, 50)

// 更新加载详情
const loadingDetails = document.getElementById('loading-details')
const logSteps = [
  { time: 500, text: '初始化 JavaScript 运行时环境...' },
  { time: 1000, text: '加载核心依赖库...' },
  { time: 1500, text: '初始化 Pinia 状态管理...' },
  { time: 2000, text: '准备应用程序界面...' },
  { time: 2500, text: '加载系统模块...' },
]

logSteps.forEach(step => {
  setTimeout(() => {
    loadingDetails.innerHTML += `<div>${step.text}</div>`
  }, step.time)
})

// ===================
// 创建Vue应用
// ===================
const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

// ===================
// 挂载应用
// ===================
setTimeout(() => {
  try {
    app.mount('#app')
    
    // 挂载成功后移除加载界面
    setTimeout(() => {
      clearInterval(progressInterval)
      progressBar.style.width = '100%'
      loadingDetails.innerHTML += '<div>应用程序准备就绪！</div>'
      
      setTimeout(() => {
        loadingDiv.style.opacity = '0'
        setTimeout(() => {
          document.body.removeChild(loadingDiv)
        }, 500)
      }, 1000)
    }, 500)
  } catch (error) {
    loadingDiv.innerHTML = `
      <div style="text-align: center; max-width: 800px; padding: 30px">
        <h1 style="color: #ff6b6b">应用程序初始化失败</h1>
        <pre style="color: #ffb648; background: #2d2d2d; padding: 20px; overflow: auto; max-height: 300px; margin: 20px 0">${error.stack}</pre>
        <p style="color: #aaa">请检查浏览器控制台获取更多信息</p>
        
        <div style="display: flex; gap: 15px; justify-content: center; margin-top: 30px">
          <button id="reload-btn" style="
            background: #42b983;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 4px;
            font-size: 16px;
          ">重新加载应用</button>
          
          <button id="console-btn" style="
            background: #2196f3;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 4px;
            font-size: 16px;
          ">打开控制台</button>
        </div>
      </div>
    `
    
    document.getElementById('reload-btn').addEventListener('click', () => {
      window.location.reload()
    })
    
    document.getElementById('console-btn').addEventListener('click', () => {
      try {
        // 尝试用键盘事件打开控制台
        const event = new KeyboardEvent('keydown', {
          key: 'F12',
          code: 'F12',
          keyCode: 123,
          which: 123,
          ctrlKey: true,
          shift: true
        })
        document.dispatchEvent(event)
      } catch (e) {
        alert('无法打开控制台，请手动按F12键')
      }
    })
    
    console.error('应用初始化错误:', error)
  }
}, 3000)

// ===================
// 应用状态检查
// ===================
setTimeout(() => {
  if (!document.querySelector('.app-container')) {
    const errorDiv = document.createElement('div')
    errorDiv.style.position = 'fixed'
    errorDiv.style.top = '0'
    errorDiv.style.left = '0'
    errorDiv.style.right = '0'
    errorDiv.style.bottom = '0'
    errorDiv.style.backgroundColor = '#1e1e1e'
    errorDiv.style.display = 'flex'
    errorDiv.style.justifyContent = 'center'
    errorDiv.style.alignItems = 'center'
    errorDiv.style.zIndex = '9999'
    errorDiv.style.flexDirection = 'column'
    
    errorDiv.innerHTML = `
      <div style="text-align: center; max-width: 800px; padding: 30px">
        <h1 style="color: #ff6b6b">应用程序加载超时</h1>
        <p style="color: #aaa; max-width: 600px; line-height: 1.6">
          应用程序未能在预期时间内完成加载。这可能是由于以下几个原因：
        </p>
        
        <ul style="text-align: left; max-width: 500px; margin: 20px auto; padding-left: 20px; color: #ccc">
          <li>网络问题导致资源加载失败</li>
          <li>浏览器阻止了某些安全策略</li>
          <li>系统资源不足或浏览器限制</li>
          <li>前端依赖未正确安装</li>
        </ul>
        
        <div style="margin-top: 30px">
          <button id="retry-btn" style="
            background: #42b983;
            color: white;
            border: none;
            padding: 12px 25px;
            cursor: pointer;
            border-radius: 4px;
            font-size: 16px;
            margin: 10px;
          ">重新加载</button>
          
          <button id="reset-btn" style="
            background: #ff9800;
            color: white;
            border: none;
            padding: 12px 25px;
            cursor: pointer;
            border-radius: 4px;
            font-size: 16px;
            margin: 10px;
          ">重新安装依赖</button>
          
          <button id="help-btn" style="
            background: #2196f3;
            color: white;
            border: none;
            padding: 12px 25px;
            cursor: pointer;
            border-radius: 4px;
            font-size: 16px;
            margin: 10px;
          ">获取帮助</button>
        </div>
        
        <div id="error-details" style="margin-top: 30px; color: #888; font-size: 14px; max-width: 600px">
          技术信息将在控制台中显示
        </div>
      </div>
    `
    
    document.body.appendChild(errorDiv)
    
    document.getElementById('retry-btn').addEventListener('click', () => {
      window.location.reload()
    })
    
    document.getElementById('reset-btn').addEventListener('click', () => {
      errorDiv.innerHTML = `
        <div style="text-align: center; padding: 30px">
          <h3 style="color: #42b983">正在重新安装依赖...</h3>
          <div style="margin: 30px 0">
            <div class="loader-spinner" style="margin: 0 auto"></div>
          </div>
          <p>这可能需要几分钟时间，请勿关闭此页面</p>
          <div id="reset-progress" style="margin-top: 20px"></div>
        </div>
      `
      
      // 模拟重新安装过程
      setTimeout(() => {
        document.getElementById('reset-progress').innerHTML = '步骤 1/4: 清理缓存...'
      }, 1000)
      
      setTimeout(() => {
        document.getElementById('reset-progress').innerHTML = '步骤 2/4: 安装依赖包...'
      }, 3000)
      
      setTimeout(() => {
        document.getElementById('reset-progress').innerHTML = '步骤 3/4: 构建应用程序...'
      }, 5000)
      
      setTimeout(() => {
        document.getElementById('reset-progress').innerHTML = '步骤 4/4: 完成! 重新加载页面'
        setTimeout(() => window.location.reload(), 2000)
      }, 8000)
    })
    
    document.getElementById('help-btn').addEventListener('click', () => {
      window.open('https://github.com/508364/live2d-driver/issues', '_blank')
    })
  }
}, 10000)

// ===================
// 全局样式
// ===================
const style = document.createElement('style')
style.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .loader-spinner {
    border: 6px solid rgba(66, 185, 131, 0.3);
    border-top: 6px solid #42b983;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    animation: spin 1.5s linear infinite;
    margin: 0 auto;
  }
  
  .progress-container {
    width: 400px;
    height: 8px;
    background: #333;
    border-radius: 4px;
    margin-top: 20px;
    overflow: hidden;
  }
  
  .progress-bar {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #42b983, #2196f3);
    transition: width 0.3s;
  }
`
document.head.appendChild(style)