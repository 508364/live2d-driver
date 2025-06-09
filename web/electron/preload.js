const { contextBridge, ipcRenderer } = require('electron')
const path = require('path')

// 暴露API给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 摄像头控制
  startTracking: () => ipcRenderer.invoke('control-tracking', true),
  stopTracking: () => ipcRenderer.invoke('control-tracking', false),
  
  // 模型管理
  setModel: (modelPath) => ipcRenderer.invoke('set-model', modelPath),
  
  // 获取模型路径
  getModelsPath: () => path.join(__dirname, '../../public/models'),
  
  // 监听事件
  onFaceData: (callback) => ipcRenderer.on('face-data', (event, data) => callback(data)),
  onFpsUpdate: (callback) => ipcRenderer.on('fps-update', (event, data) => callback(data))
})