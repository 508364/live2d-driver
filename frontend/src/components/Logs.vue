<template>
  <div class="logs-page">
    <div class="log-controls">
      <button @click="clearLogs" class="log-button clear-btn">
        <span>清空日志</span>
      </button>
      <button @click="exportLogs" class="log-button export-btn">
        <span>导出日志</span>
      </button>
    </div>
    
    <div class="log-content">
      <div v-for="(log, index) in logs" :key="index" class="log-entry" :class="log.type">
        <span class="log-timestamp">[{{ formatTime(log.timestamp) }}]</span>
        <span class="log-message">{{ log.message }}</span>
      </div>
      
      <div v-if="logs.length === 0" class="no-logs">
        暂无日志记录
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useLogStore } from '../stores/logs'

export default {
  setup() {
    const logStore = useLogStore()
    
    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`
    }
    
    const clearLogs = () => {
      logStore.clearLogs()
    }
    
    const exportLogs = () => {
      logStore.exportLogs()
    }
    
    return {
      logs: computed(() => logStore.logs),
      formatTime,
      clearLogs,
      exportLogs
    }
  }
}
</script>

<style scoped>
.logs-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.log-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.log-button {
  padding: 10px 15px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
  border: none;
}

.clear-btn {
  background: rgba(255, 99, 99, 0.2);
  color: #ff6363;
}

.clear-btn:hover {
  background: #ff6363;
  color: white;
}

.export-btn {
  background: rgba(66, 185, 131, 0.2);
  color: #42b983;
}

.export-btn:hover {
  background: #42b983;
  color: white;
}

.log-content {
  flex: 1;
  background: var(--card-bg);
  border-radius: 8px;
  padding: 15px;
  overflow-y: auto;
  font-family: monospace;
  font-size: 14px;
  min-height: 300px;
}

.log-entry {
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.log-entry:last-child {
  border-bottom: none;
}

.log-timestamp {
  color: #aaa;
  margin-right: 15px;
}

.log-entry.info .log-message {
  color: var(--text-color);
}

.log-entry.warning .log-message {
  color: #ffb648;
}

.log-entry.error .log-message {
  color: #ff6b6b;
}

.no-logs {
  text-align: center;
  padding: 40px;
  color: #666;
}
</style>