<template>
  <div class="settings-page">
    <div class="settings-section">
      <h3>主题预设</h3>
      <div class="theme-presets">
        <div 
          v-for="theme in themes" 
          :key="theme.id" 
          class="theme-option"
          :class="{ active: selectedTheme === theme.id }"
          @click="selectTheme(theme.id)"
        >
          <div class="theme-preview" :style="themeStyle(theme)"></div>
          <div class="theme-name">{{ theme.name }}</div>
        </div>
      </div>
    </div>
    
    <div class="settings-section">
      <h3>自定义主题</h3>
      <div class="custom-theme">
        <div v-for="(value, name) in themeColors" :key="name" class="color-picker">
          <label>{{ keyMap[name] }}</label>
          <input type="color" v-model="themeColors[name]">
          <span class="color-value">{{ themeColors[name] }}</span>
        </div>
      </div>
      <button class="apply-theme" @click="applyCustomTheme">保存自定义主题</button>
    </div>
    
    <div class="settings-section">
      <h3>其他设置</h3>
      <div class="general-settings">
        <div class="setting-item">
          <label>自动启动摄像头</label>
          <label class="toggle-switch">
            <input type="checkbox" v-model="autoStartCamera">
            <span class="slider"></span>
          </label>
        </div>
        
        <div class="setting-item">
          <label>显示FPS计数</label>
          <label class="toggle-switch">
            <input type="checkbox" v-model="showFpsCounter" checked>
            <span class="slider"></span>
          </label>
        </div>
        
        <div class="setting-item">
          <label>默认模型</label>
          <select v-model="defaultModel" class="model-select">
            <option value="haru">Haru</option>
            <option value="miku">Miku</option>
            <option value="satori">Satori</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useThemeStore } from '../stores/theme'

export default {
  setup() {
    const themeStore = useThemeStore()
    
    const themes = ref([
      { id: 'dark', name: '深色主题', primary: '#42b983', background: '#1e1e1e', sidebar: '#252525', text: '#ffffff' },
      { id: 'light', name: '浅色主题', primary: '#42b983', background: '#ffffff', sidebar: '#f5f5f5', text: '#333333' },
      { id: 'blue', name: '蓝色主题', primary: '#2196f3', background: '#0d47a1', sidebar: '#1a237e', text: '#ffffff' }
    ])
    
    const themeColors = ref({ ...themeStore.customTheme })
    const selectedTheme = ref(themeStore.currentTheme)
    
    const keyMap = {
      primary: '主色调',
      background: '背景色',
      sidebar: '侧边栏',
      text: '文字颜色',
      cardBg: '卡片背景'
    }
    
    // 其他设置
    const autoStartCamera = ref(false)
    const showFpsCounter = ref(true)
    const defaultModel = ref('haru')
    
    const themeStyle = (theme) => {
      return {
        background: `linear-gradient(45deg, ${theme.background} 0%, ${theme.primary} 100%)`,
        borderColor: theme.primary
      }
    }
    
    const selectTheme = (themeId) => {
      selectedTheme.value = themeId
      if (themeId !== 'custom') {
        themeStore.setTheme(themeId)
      }
    }
    
    const applyCustomTheme = () => {
      themeStore.setCustomTheme(themeColors.value)
      selectedTheme.value = 'custom'
      themeStore.setTheme('custom')
    }
    
    return {
      themes,
      themeColors,
      selectedTheme,
      keyMap,
      autoStartCamera,
      showFpsCounter,
      defaultModel,
      themeStyle,
      selectTheme,
      applyCustomTheme
    }
  }
}
</script>

<style scoped>
.settings-page {
  height: 100%;
  overflow-y: auto;
  padding: 10px;
}

.settings-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.settings-section h3 {
  margin-top: 0;
  color: var(--primary-color);
}

.theme-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 10px;
}

.theme-option {
  width: 130px;
  cursor: pointer;
  text-align: center;
  transition: transform 0.3s;
}

.theme-option:hover {
  transform: translateY(-5px);
}

.theme-option.active {
  transform: translateY(-5px);
  font-weight: bold;
}

.theme-preview {
  width: 100%;
  height: 70px;
  border-radius: 8px;
  border: 2px solid #888;
  margin-bottom: 8px;
  transition: all 0.3s;
}

.theme-option.active .theme-preview {
  border-color: var(--primary-color);
  box-shadow: 0 0 10px rgba(66, 185, 131, 0.5);
}

.theme-name {
  font-size: 14px;
}

.custom-theme {
  margin: 15px 0;
}

.color-picker {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.color-picker label {
  width: 100px;
}

.color-picker input[type="color"] {
  width: 50px;
  height: 30px;
  margin-right: 15px;
  cursor: pointer;
}

.color-value {
  font-family: monospace;
  font-size: 14px;
  color: #aaa;
}

.apply-theme {
  margin-top: 15px;
  padding: 10px 20px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
}

.apply-theme:hover {
  opacity: 0.9;
  transform: translateY(-2px);
}

.general-settings {
  margin-top: 15px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.setting-item:last-child {
  border-bottom: none;
}

.model-select {
  padding: 8px;
  background: rgba(255,255,255,0.1);
  border: 1px solid #555;
  border-radius: 4px;
  color: var(--text-color);
  cursor: pointer;
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