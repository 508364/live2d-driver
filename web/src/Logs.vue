<template>
  <div class="logs-page">
    <h2 class="page-title">
      <span class="log-icon">📝</span> 日志
    </h2>
    
    <div class="log-controls">
      <button class="clear-btn" @click="clearLogs">
        <span>清空日志</span>
      </button>
      <button class="export-btn" @click="exportLogs">
        <span>导出日志</span>
      </button>
    </div>
    
    <div class="log-content">
      <!-- 根据截图1，日志区域显示空白 -->
      <p class="empty-hint">暂无日志内容</p>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    clearLogs() {
      console.log("清空日志操作");
    },
    exportLogs() {
      console.log("导出日志操作");
    }
  }
}
</script>

<style scoped>
.logs-page {
  padding: 20px;
  color: white;
}

.page-title {
  display: flex;
  align-items: center;
  font-size: 24px;
  margin-bottom: 20px;
}

.log-icon {
  margin-right: 10px;
  font-size: 28px;
}

.log-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.clear-btn, .export-btn {
  padding: 10px 15px;
  background: #2d2d2d;
  border: 1px solid #444;
  border-radius: 6px;
  color: #aaa;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.clear-btn:hover {
  background: #ff6b6b;
  color: white;
}

.export-btn:hover {
  background: #42b983;
  color: white;
}

.log-content {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
}

.empty-hint {
  color: #666;
  font-size: 16px;
}
</style>