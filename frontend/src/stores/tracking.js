import { defineStore } from 'pinia'

export const useTrackingStore = defineStore('tracking', {
  state: () => ({
    isRunning: false,
    fps: 0,
    faceData: null,
    cameraAccess: false,
    parameters: {
      headX: 0,
      headY: 0,
      eyeX: 0,
      eyeY: 0,
      mouth: 0,
      eyebrowLeft: 0,
      eyebrowRight: 0
    }
  }),
  actions: {
    startTracking() {
      this.isRunning = true
      this.resetParameters()
    },
    stopTracking() {
      this.isRunning = false
      this.resetParameters()
    },
    resetParameters() {
      this.parameters = {
        headX: 0,
        headY: 0,
        eyeX: 0,
        eyeY: 0,
        mouth: 0,
        eyebrowLeft: 0,
        eyebrowRight: 0
      }
    },
    updateFps(fps) {
      this.fps = fps
    },
    updateFaceData(faceData) {
      this.faceData = faceData
      
      if (faceData) {
        // 模拟参数更新（实际实现需要面部特征点计算）
        this.parameters.headX = (faceData.x / window.innerWidth).toFixed(3)
        this.parameters.headY = (faceData.y / window.innerHeight).toFixed(3)
        
        // 使用landmarks计算更精细的参数
        if (faceData.landmarks && faceData.landmarks.length > 0) {
          // 眼睛开合度（简化计算）
          const leftEyeHeight = Math.abs(faceData.landmarks[1][1] - faceData.landmarks[5][1])
          const rightEyeHeight = Math.abs(faceData.landmarks[2][1] - faceData.landmarks[4][1])
          this.parameters.eyeY = ((leftEyeHeight + rightEyeHeight) / 20).toFixed(3)
          
          // 嘴巴开合度
          const mouthHeight = Math.abs(faceData.landmarks[3][1] - faceData.landmarks[6][1])
          this.parameters.mouth = (mouthHeight / 10).toFixed(3)
        }
      }
    }
  }
})