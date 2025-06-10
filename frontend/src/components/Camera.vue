<template>
  <div class="camera-page">
    <div class="preview-container">
      <div class="preview-label">虚拟摄像头输出</div>
      <video ref="outputVideo" autoplay muted></video>
    </div>
    
    <div class="controls">
      <div class="control-group">
        <label>
          <span>推流状态</span>
          <label class="toggle-switch">
            <input type="checkbox" v-model="isStreaming" @change="toggleStreaming">
            <span class="slider"></span>
          </label>
        </label>
      </div>
      
      <div class="control-group">
        <label>
          <span>显示背景</span>
          <label class="toggle-switch">
            <input type="checkbox" v-model="showBackground">
            <span class="slider"></span>
          </label>
        </label>
      </div>
      
      <div class="control-group">
        <label>
          <span>摄像头名称</span>
          <input 
            type="text" 
            v-model="cameraName" 
            placeholder="设置虚拟摄像头名称"
            class="name-input"
          >
        </label>
      </div>
      
      <div class="control-group">
        <label>
          <span>视频流地址</span>
          <code>{{ streamUrl }}</code>
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useLogStore } from '../stores/logs'

export default {
  setup() {
    const isStreaming = ref(false)
    const showBackground = ref(false)
    const cameraName = ref('Live2D Virtual Camera')
    const streamUrl = ref('未推流')
    const outputVideo = ref(null)
    const logStore = useLogStore()
    
    let mediaRecorder = null
    let recordedChunks = []
    
    const toggleStreaming = () => {
      if (isStreaming.value) {
        startStreaming()
      } else {
        stopStreaming()
      }
    }
    
    const startStreaming = () => {
      if (!isStreaming.value) return
      
      // 创建虚拟视频流
      const stream = createVirtualStream()
      
      if (stream) {
        outputVideo.value.srcObject = stream
        startRecording(stream)
        streamUrl.value = 'http://localhost:3000/live2d.webm'
        logStore.addLog('虚拟摄像头启动')
      }
    }
    
    const createVirtualStream = () => {
      try {
        const canvas = document.createElement('canvas')
        canvas.width = 1280
        canvas.height = 720
        const ctx = canvas.getContext('2d')
        
        // 绘制简单背景
        ctx.fillStyle = showBackground.value ? '#252525' : '#000'
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        
        // 绘制文字
        ctx.fillStyle = '#42b983'
        ctx.font = '40px Arial'
        ctx.textAlign = 'center'
        ctx.fillText('Live2D 虚拟摄像头', canvas.width/2, canvas.height/2)
        
        // 创建视频流
        return canvas.captureStream(30)
      } catch (err) {
        logStore.addLog(`创建虚拟流失败: ${err.message}`, 'error')
        return null
      }
    }
    
    const startRecording = (stream) => {
      recordedChunks = []
      
      try {
        mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'video/webm;codecs=vp9'
        })
        
        mediaRecorder.ondataavailable = (event) => {
          if (event.data && event.data.size > 0) {
            recordedChunks.push(event.data)
          }
        }
        
        mediaRecorder.start(100)
        
        logStore.addLog('视频流开始录制')
      } catch (err) {
        logStore.addLog(`媒体录制失败: ${err.message}`, 'error')
      }
    }
    
    const stopStreaming = () => {
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop()
      }
      
      if (outputVideo.value.srcObject) {
        outputVideo.value.srcObject.getTracks().forEach(track => track.stop())
        outputVideo.value.srcObject = null
      }
      
      isStreaming.value = false
      streamUrl.value = '未推流'
      logStore.addLog('虚拟摄像头停止')
    }
    
    onMounted(() => {
      // 创建模拟视频源
      const stream = createVirtualStream()
      if (stream) {
        outputVideo.value.srcObject = stream
      }
    })
    
    return {
      isStreaming,
      showBackground,
      cameraName,
      streamUrl,
      outputVideo,
      toggleStreaming
    }
  }
}
</script>

<style scoped>
.camera-page {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.preview-container {
  position: relative;
  width: 100%;
  max-width: 800px;
  height: 450px;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  margin: 0 auto 20px;
  border: 2px solid var(--primary-color);
}

.preview-label {
  position: absolute;
  top: 5px;
  left: 5px;
  background: rgba(0,0,0,0.7);
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 14px;
  z-index: 10;
}

.preview-container video {
  width: 100%;
  height: 100%;
  display: block;
}

.controls {
  background: var(--card-bg);
  padding: 20px;
  border-radius: 8px;
}

.control-group {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.control-group label {
  display: flex;
  align-items: center;
  width: 100%;
}

.control-group span {
  min-width: 100px;
  display: inline-block;
}

.name-input {
  padding: 8px 12px;
  background: rgba(255,255,255,0.1);
  border: 1px solid #555;
  border-radius: 4px;
  color: var(--text-color);
  flex: 1;
}

.name-input::placeholder {
  color: #aaa;
}

code {
  background: rgba(255,255,255,0.1);
  padding: 8px;
  border-radius: 4px;
  color: var(--primary-color);
  font-family: monospace;
  word-break: break-all;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #555;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--primary-color);
}

input:checked + .slider:before {
  transform: translateX(26px);
}
</style>