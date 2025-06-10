import { defineStore } from 'pinia'

export const useLogStore = defineStore('logs', {
  state: () => ({
    logs: JSON.parse(localStorage.getItem('app-logs')) || [
      { 
        timestamp: new Date().toISOString(), 
        message: '应用程序启动',
        type: 'info'
      }
    ]
  }),
  actions: {
    addLog(message, type = 'info') {
      const logEntry = {
        timestamp: new Date().toISOString(),
        message,
        type
      }
      
      this.logs.push(logEntry)
      
      // 保持最多500条日志
      if (this.logs.length > 500) {
        this.logs.shift()
      }
      
      localStorage.setItem('app-logs', JSON.stringify(this.logs))
    },
    
    clearLogs() {
      this.logs = [{
        timestamp: new Date().toISOString(),
        message: '日志已清空',
        type: 'info'
      }]
      localStorage.setItem('app-logs', JSON.stringify(this.logs))
    },
    
    exportLogs() {
      const logContent = this.logs.map(log => 
        `[${new Date(log.timestamp).toLocaleString()}] ${log.type.toUpperCase()}: ${log.message}`
      ).join('\n')
      
      const blob = new Blob([logContent], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `live2d-logs-${new Date().toISOString().slice(0, 10)}.txt`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      this.addLog('日志已导出')
    }
  }
})