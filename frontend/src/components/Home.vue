<template>
  <div class="home">
    <!-- 状态栏 -->
    <div class="status-card" :class="{ 'status-active': isTracking }">
      <span class="status-icon">●</span>
      {{ statusMessage }}
    </div>
    
    <!-- 主控制按钮 -->
    <button 
      @click="toggleTracking" 
      :class="['track-button', { active: isTracking }]"
    >
      {{ isTracking ? '停止面捕、动捕' : '启动面捕、动捕' }}
    </button>
    
    <!-- FPS计数器 -->
    <div class="fps-counter">
      实时FPS: {{ fps }}
    </div>
    
    <!-- 摄像头预览 -->
    <div class="camera-preview">
      <div class="preview-label">实时摄像头画面</div>
      <video ref="cameraFeed" autoplay muted></video>
      <canvas ref="detectionCanvas" class="detection-overlay"></canvas>
    </div>
    
    <!-- Live2D模型显示区 -->
    <div class="live2d-container">
      <div class="preview-label">Live2D形象预览</div>
      <canvas ref="live2dCanvas" width="640" height="480"></canvas>
    </div>
    
    <!-- 隐藏视频用于面部检测 -->
    <video ref="hiddenVideo" autoplay muted style="display: none;"></video>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useLogStore } from '../stores/logs'
import { init, startDetection, stopDetection } from '../faceDetection'
import { useTrackingStore } from '../stores/tracking'
const trackingStore = useTrackingStore()

export default {
  setup() {
    const cameraFeed = ref(null)
    const hiddenVideo = ref(null)
    const detectionCanvas = ref(null)
    const live2dCanvas = ref(null)
    const isTracking = ref(false)
    const statusMessage = ref('准备就绪')
    const fps = ref('--')
    const logStore = useLogStore()
    
    let animationFrameId = null
    let lastFace = null
    let frameCount = 0
    let lastTime = 0
    
    // 初始化面部检测
    const initFaceDetection = async () => {
      try {
        const success = await init()
        if (success) {
          logStore.addLog('面部检测模型加载成功')
          return true
        } else {
          logStore.addLog('面部检测模型加载失败', 'error')
          return false
        }
      } catch (error) {
        logStore.addLog(`面部检测初始化错误: ${error.message}`, 'error')
        return false
      }
    }
    
    // 开始追踪
    const startTracking = async () => {
      try {
        statusMessage.value = '正在启动摄像头...'
        
        // 获取摄像头权限
        const stream = await navigator.mediaDevices.getUserMedia({ video: true })
        cameraFeed.value.srcObject = stream
        hiddenVideo.value.srcObject = stream
        
        // 初始化面部检测
        const detectionReady = await initFaceDetection()
        
        if (detectionReady) {
          // 启动检测
          startDetection(hiddenVideo.value, (faceData) => {
            lastFace = faceData
            
            // 在预览上绘制检测结果
            if (detectionCanvas.value) {
              const ctx = detectionCanvas.value.getContext('2d')
              const { width, height } = detectionCanvas.value
              ctx.clearRect(0, 0, width, height)
              
            if (faceData) {
              trackingStore.updateFaceData(faceData)
              } else {
              trackingStore.updateFaceData(null)
              }
              
              // 绘制检测框
              if (faceData && faceData.box) {
                ctx.strokeStyle = 'red'
                ctx.lineWidth = 2
                ctx.strokeRect(faceData.box.x, faceData.box.y, faceData.box.width, faceData.box.height)
              }
              
              // 更新Live2D模型
              updateLive2DModel(faceData) 
            }
          })
          
          // 开始FPS计数
          startFpsCounter()
          
          statusMessage.value = '追踪中...'
          isTracking.value = true
          logStore.addLog('面捕、动捕启动')
          
          return true
        }
      } catch (error) {
        statusMessage.value = `错误: ${error.message}`
        logStore.addLog(`摄像头启动失败: ${error.message}`, 'error')
        return false
      }
    }
    
    // 停止追踪
    const stopTracking = () => {
      if (cameraFeed.value.srcObject) {
        const tracks = cameraFeed.value.srcObject.getTracks()
        tracks.forEach(track => track.stop())
        cameraFeed.value.srcObject = null
      }
      
      // 停止检测
      stopDetection()
      
      // 停止FPS计数
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId)
        animationFrameId = null
      }
      
      statusMessage.value = '已停止'
      isTracking.value = false
      fps.value = '--'
      logStore.addLog('面捕、动捕停止')
    }
    
    // 切换追踪状态
    const toggleTracking = async () => {
      if (isTracking.value) {
        stopTracking()
      } else {
        await startTracking()
      }
    }
    
    // 更新Live2D模型
    const updateLive2DModel = (faceData) => {
      if (!live2dCanvas.value) return
      
      const ctx = live2dCanvas.value.getContext('2d')
      ctx.clearRect(0, 0, live2dCanvas.value.width, live2dCanvas.value.height)
      
      // 简单模拟Live2D模型更新
      ctx.fillStyle = '#42b983'
      ctx.font = '24px Arial'
      ctx.textAlign = 'center'
      ctx.fillText('Live2D模型驱动中...', live2dCanvas.value.width / 2, live2dCanvas.value.height / 2)
      
      // 在实际项目中，这里会调用Live2D SDK更新模型状态
    }
    
    // FPS计数器
    const startFpsCounter = () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId)
      }
      
      frameCount = 0
      lastTime = performance.now()
      
      const calculateFps = (timestamp) => {
        frameCount++
        const elapsed = timestamp - lastTime
        
        if (elapsed >= 1000) {
          fps.value = Math.round((frameCount * 1000) / elapsed)
          trackingStore.updateFps(fps.value)
        }
        
        animationFrameId = requestAnimationFrame(calculateFps)
      }
      
      animationFrameId = requestAnimationFrame(calculateFps)
    }
    
    // 组件挂载时初始化
    onMounted(async () => {
      // 设置canvas尺寸匹配视频
      const setCanvasSize = () => {
        if (cameraFeed.value) {
          const videoWidth = cameraFeed.value.videoWidth || 640
          const videoHeight = cameraFeed.value.videoHeight || 480
          
          if (detectionCanvas.value) {
            detectionCanvas.value.width = videoWidth
            detectionCanvas.value.height = videoHeight
          }
        }
      }
      
      cameraFeed.value.addEventListener('loadedmetadata', setCanvasSize)
    })
    
    // 组件卸载时清理
    onUnmounted(() => {
      if (isTracking.value) {
        trackingStore.startTracking()
      } else {
        trackingStore.stopTracking()
      }
    })

    return {
      cameraFeed,
      hiddenVideo,
      detectionCanvas,
      live2dCanvas,
      isTracking,
      statusMessage,
      fps,
      toggleTracking
    }
  }
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.status-card {
  background: var(--card-bg);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 16px;
  display: flex;
  align-items: center;
  border-left: 4px solid #555;
}

.status-card.status-active {
  border-left: 4px solid var(--primary-color);
}

.status-icon {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #aaa;
  margin-right: 10px;
}

.status-card.status-active .status-icon {
  background: var(--primary-color);
}

.track-button {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: all 0.3s;
  margin-bottom: 20px;
  width: 200px;
}

.track-button.active {
  background: #dc3545;
}

.track-button:hover {
  opacity: 0.9;
  transform: translateY(-2px);
}

.fps-counter {
  margin-bottom: 20px;
  color: var(--primary-color);
  font-weight: bold;
}

.camera-preview {
  position: relative;
  width: 100%;
  max-width: 640px;
  height: 480px;
  border: 2px solid var(--primary-color);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
  background: #000;
}

.preview-label {
  position: absolute;
  top: 5px;
  left: 5px;
  background: rgba(0,0,0,0.5);
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 10;
}

.camera-preview video {
  width: 100%;
  height: 100%;
}

.detection-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 5;
}

.live2d-container {
  flex: 1;
  background: var(--card-bg);
  border-radius: 8px;
  margin-top: 20px;
  position: relative;
  overflow: hidden;
}

.live2d-container canvas {
  width: 100%;
  height: 100%;
}
</style>