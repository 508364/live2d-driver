const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const WebSocket = require('ws')

let pythonProcess = null
let mainWindow = null
let ws = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    darkTheme: true,
    backgroundColor: '#1e1e1e',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      enableRemoteModule: false
    }
  })

  mainWindow.loadFile(path.join(__dirname, '../../public/index.html'))
  
  // 启动Python后端
  startPythonBackend()
  
  // 打开开发者工具（开发环境）
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools()
  }
}

function startPythonBackend() {
  if (pythonProcess) return
  
  // 根据平台设置Python命令
  const pythonCmd = process.platform === 'win32' ? 'python' : 'python3'
  pythonProcess = spawn(pythonCmd, [path.join(__dirname, '../../../python/main.py')])
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`[Python] ${data}`)
  })
  
  pythonProcess.stderr.on('data', (data) => {
    console.error(`[Python ERROR] ${data}`)
  })
  
  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`)
    pythonProcess = null
    // 尝试重新连接
    setTimeout(connectToPython, 1000)
  })
  
  // 连接到Python WebSocket
  connectToPython()
}

function connectToPython() {
  if (ws && ws.readyState !== WebSocket.CLOSED) return
  
  ws = new WebSocket('ws://localhost:50836')
  
  ws.on('open', () => {
    console.log('Connected to Python backend')
  })
  
  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data)
      switch (message.type) {
        case 'face_data':
          mainWindow.webContents.send('face-data', message.data)
          break
        case 'fps':
          mainWindow.webContents.send('fps-update', message.data)
          break
      }
    } catch (err) {
      console.error('Error parsing WebSocket message:', err)
    }
  })
  
  ws.on('error', (err) => {
    console.error('WebSocket error:', err)
  })
  
  ws.on('close', () => {
    console.log('Disconnected from Python backend')
    // 尝试重新连接
    setTimeout(connectToPython, 1000)
  })
}

// 处理来自渲染进程的命令
ipcMain.handle('control-tracking', (_, isTracking) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      command: isTracking ? 'start_tracking' : 'stop_tracking'
    }))
    return true
  }
  return false
})

ipcMain.handle('set-model', (_, modelPath) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      command: 'set_model',
      path: modelPath
    }))
    return true
  }
  return false
})

app.whenReady().then(() => {
  createWindow()
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (pythonProcess) {
    pythonProcess.kill()
    pythonProcess = null
  }
  
  if (process.platform !== 'darwin') {
    app.quit()
  }
})