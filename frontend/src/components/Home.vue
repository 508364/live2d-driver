<!-- frontend/src/components/Home.vue -->
<template>
  <div class="home-container">
    <div class="camera-preview">
      <!-- 这里显示摄像头画面 -->
      <div class="camera-placeholder">
        <div class="placeholder-text">
          <span v-if="trackingActive">👁 正在追踪面部运动...</span>
          <span v-else>📷 点击"开始追踪"启动摄像头</span>
        </div>
        <div class="fps-counter">FPS: {{ fps }}</div>
      </div>
    </div>
    
    <div class="controls">
      <button class="control-btn" @click="toggleTracking">
        {{ trackingActive ? '⏹️ 停止追踪' : '▶️ 开始追踪' }}
      </button>
      <button class="control-btn" @click="resetPosition">🔁 重置位置</button>
    </div>
    
    <div class="tracking-data">
      <h3>追踪数据</h3>
      <div class="data-grid">
        <div class="data-item">
          <span class="data-label">面部位置:</span>
          <span class="data-value">{{ facePosition.x }}, {{ facePosition.y }}</span>
        </div>
        <div class="data-item">
          <span class="data-label">眼睛状态:</span>
          <span class="data-value">{{ eyeState }}</span>
        </div>
        <div class="data-item">
          <span class="data-label">嘴巴状态:</span>
          <span class="data-value">{{ mouthState }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useTrackingStore } from '../stores/tracking'
import * as tf from '@tensorflow/tfjs'
import * as blazeface from '@tensorflow-models/blazeface'

export default {
  data() {
    return {
      trackingActive: false,
      fps: 0,
      facePosition: { x: 0, y: 0 },
      eyeState: '正常',
      mouthState: '闭合',
      faceDetector: null,
      animationFrameId: null,
      lastFrameTime: 0,
      frameCount: 0
    }
  },
  mounted() {
    this.initFaceDetection()
  },
  beforeUnmount() {
    this.stopTracking()
  },
  methods: {
    async initFaceDetection() {
      try {
        // 加载TensorFlow模型
        await tf.ready()
        this.faceDetector = await blazeface.load()
        console.log('人脸检测模型加载成功')
      } catch (error) {
        console.error('模型加载失败:', error)
      }
    },
    
    startFaceTracking() {
      if (!this.faceDetector) {
        console.error('人脸检测模型未加载')
        return
      }
      
      this.trackingActive = true
      this.trackFace()
    },
    
    async trackFace() {
      if (!this.trackingActive) return
      
      const now = performance.now()
      const elapsed = now - this.lastFrameTime
      
      if (elapsed > 100) {
        try {
          // 这里应该获取真实的视频帧
          // 模拟检测过程
          const predictions = await this.faceDetector.estimateFaces(document.createElement('canvas'))
          
          if (predictions.length > 0) {
            const face = predictions[0]
            this.facePosition = {
              x: Math.round(face.topLeft[0]),
              y: Math.round(face.topLeft[1])
            }
            
            // 模拟眼睛和嘴巴状态
            this.eyeState = Math.random() > 0.5 ? '睁开' : '眨眼'
            this.mouthState = Math.random() > 0.7 ? '张开' : '闭合'
          }
          
          // 更新FPS计数器
          if (elapsed >= 1000) {
            this.fps = Math.round((this.frameCount * 1000) / elapsed)
            this.frameCount = 0
            this.lastFrameTime = now
          } else {
            this.frameCount++
          }
        } catch (error) {
          console.error('面部检测出错:', error)
        }
      }
      
      this.animationFrameId = requestAnimationFrame(this.trackFace)
    },
    
    stopFaceTracking() {
      this.trackingActive = false
      if (this.animationFrameId) {
        cancelAnimationFrame(this.animationFrameId)
        this.animationFrameId = null
      }
      this.resetPosition()
    },
    
    resetPosition() {
      this.facePosition = { x: 0, y: 0 }
      this.eyeState = '正常'
      this.mouthState = '闭合'
    },
    
    toggleTracking() {
      if (this.trackingActive) {
        this.stopFaceTracking()
      } else {
        this.startFaceTracking()
      }
      this.$emit('tracking-toggled', this.trackingActive)
    }
  }
}
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
}

.camera-preview {
  flex: 1;
  background: #1a1a1a;
  border-radius: 8px;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
  border: 1px solid #444;
}

.camera-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2a2a2a 25%, #333 25%, #333 50%, #2a2a2a 50%, #2a2a2a 75%, #333 75%, #333);
  background-size: 20px 20px;
}

.placeholder-text {
  font-size: 24px;
  color: #888;
  text-align: center;
  padding: 20px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 8px;
}

.fps-counter {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: #42b983;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 14px;
}

.controls {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.control-btn {
  flex: 1;
  padding: 15px;
  border: none;
  border-radius: 8px;
  background: #42b983;
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: background 0.2s;
}

.control-btn:hover {
  background: #3ca474;
}

.tracking-data {
  background: #2d2d2d;
  border-radius: 8px;
  padding: 15px;
  border: 1px solid #444;
}

.tracking-data h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #42b983;
  border-bottom: 1px solid #444;
  padding-bottom: 10px;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.data-item {
  background: rgba(255, 255, 255, 0.05);
  padding: 10px;
  border-radius: 6px;
}

.data-label {
  font-weight: bold;
  color: #888;
  margin-right: 10px;
}

.data-value {
  color: #42b983;
  font-weight: 500;
}
</style>