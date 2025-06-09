<template>
  <div class="settings-page">
    <h2 class="page-title">
      <span class="settings-icon">⚙️</span> 设置
    </h2>
    
    <div class="settings-section">
      <h3>主题预设</h3>
      <div class="theme-presets">
        <div class="theme-option" v-for="theme in themes" :key="theme.id">
          <div class="theme-preview" :style="themeStyle(theme)"></div>
          <div class="theme-name">{{ theme.name }}</div>
        </div>
      </div>
    </div>
    
    <!-- 根据截图3，设置页面其余区域为空白 -->
    <div class="empty-hint">更多设置选项将在此显示</div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      themes: [
        { id: 'dark', name: '深色主题' },
        { id: 'blue', name: '蓝色主题' }
      ]
    }
  },
  methods: {
    themeStyle(theme) {
      return {
        background: theme.id === 'dark' ? '#252525' : '#1a237e',
        border: theme.id === 'dark' ? '2px solid #42b983' : '2px solid #2196f3'
      }
    }
  }
}
</script>

<style scoped>
.settings-page {
  padding: 20px;
  color: white;
}

.page-title {
  display: flex;
  align-items: center;
  font-size: 24px;
  margin-bottom: 20px;
}

.settings-icon {
  margin-right: 10px;
}

.settings-section {
  margin-bottom: 30px;
}

.settings-section h3 {
  font-size: 18px;
  margin-bottom: 15px;
  color: #aaa;
}

.theme-presets {
  display: flex;
  gap: 20px;
}

.theme-option {
  width: 120px;
  text-align: center;
}

.theme-preview {
  width: 100%;
  height: 70px;
  border-radius: 8px;
  margin-bottom: 10px;
}

.theme-name {
  color: #aaa;
}

.empty-hint {
  padding: 40px;
  text-align: center;
  color: #666;
  background: #1e1e1e;
  border-radius: 8px;
}
</style>