import * as tf from '@tensorflow/tfjs'
import * as blazeface from '@tensorflow-models/blazeface'

let model = null
let isRunning = false
let callback = null
let animationFrameId = null

export async function init() {
  try {
    await tf.setBackend('webgl')
    model = await blazeface.load()
    return true
  } catch (error) {
    console.error('面部检测模型加载失败:', error)
    return false
  }
}

export function startDetection(video, onFaceDetected) {
  if (!model || isRunning) return false
  
  isRunning = true
  callback = onFaceDetected
  video.width = video.videoWidth
  video.height = video.videoHeight
  
  const detectFrame = async () => {
    if (!isRunning) return
    
    try {
      const predictions = await model.estimateFaces(video, false)
      
      if (predictions.length > 0) {
        const face = predictions[0]
        callback({
          x: face.topLeft[0],
          y: face.topLeft[1],
          width: face.bottomRight[0] - face.topLeft[0],
          height: face.bottomRight[1] - face.topLeft[1],
          landmarks: face.landmarks
        })
      } else {
        callback(null)
      }
    } catch (error) {
      console.error('面部检测出错:', error)
    }
    
    animationFrameId = requestAnimationFrame(detectFrame)
  }
  
  detectFrame()
  return true
}

export function stopDetection() {
  isRunning = false
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
}