<template>
  <div class="upload-page">
    <div class="upload-area" @click="triggerFileUpload">
      <div class="upload-hint">
        <span class="upload-icon">📁</span>
        <p>点击或拖放文件夹/.zip文件到此处</p>
      </div>
      <input 
        type="file" 
        ref="fileInput" 
        style="display: none" 
        @change="handleFileUpload"
        accept=".zip,.model" 
      >
    </div>
    
    <div class="model-list">
      <div class="model-item" v-for="(model, index) in models" :key="index">
        <div class="model-info">
          <h3>{{ model.name }}</h3>
          <p>{{ model.size }}</p>
        </div>
        <button 
          class="use-model-btn" 
          @click="useModel(model)"
          :class="{ active: activeModel === model.path }"
        >
          <span>使用形象</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useLogStore } from '../stores/logs'

export default {
  setup() {
    const models = ref([
      { 
        name: 'Haru', 
        size: '4.07 MB', 
        path: 'models/Haru/model.json',
        date: '2023-10-15' 
      }
    ])
    
    const activeModel = ref('')
    const logStore = useLogStore()
    
    const triggerFileUpload = () => {
      fileInput.value.click()
    }
    
    const handleFileUpload = (event) => {
      const files = event.target.files
      if (!files || files.length === 0) return
      
      const file = files[0]
      const fileName = file.name.replace(/\.[^/.]+$/, "") // 去除扩展名
      const fileSize = (file.size / (1024 * 1024)).toFixed(2) + ' MB'
      
      // 模拟上传处理
      const newModel = {
        name: fileName,
        size: fileSize,
        path: `models/${fileName}/model.json`,
        date: new Date().toLocaleDateString()
      }
      
      models.value.unshift(newModel)
      logStore.addLog(`已上传模型: ${fileName} (${fileSize})`)
      
      // 在实际项目中，这里会上传模型文件到服务器或本地存储
    }
    
    const useModel = (model) => {
      activeModel.value = model.path
      logStore.addLog(`已选择模型: ${model.name}`)
      // 在实际项目中，这里会加载并设置新的Live2D模型
    }
    
    return {
      models,
      activeModel,
      triggerFileUpload,
      handleFileUpload,
      useModel
    }
  }
}
</script>

<style scoped>
.upload-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.upload-area {
  border: 2px dashed var(--primary-color);
  border-radius: 8px;
  padding: 60px 20px;
  text-align: center;
  margin-bottom: 20px;
  background: var(--card-bg);
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  background: rgba(66, 185, 131, 0.1);
  transform: translateY(-2px);
}

.upload-hint {
  color: #aaa;
}

.upload-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 15px;
}

.model-list {
  flex: 1;
  overflow-y: auto;
  background: var(--card-bg);
  border-radius: 8px;
  padding: 15px;
}

.model-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  transition: background 0.3s;
}

.model-item:hover {
  background: rgba(255,255,255,0.05);
}

.model-item:last-child {
  border-bottom: none;
}

.model-info {
  flex: 1;
}

.model-info h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.model-info p {
  margin: 0;
  color: #aaa;
  font-size: 14px;
}

.use-model-btn {
  background: rgba(66, 185, 131, 0.2);
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
  border-radius: 4px;
  padding: 8px 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.use-model-btn:hover, .use-model-btn.active {
  background: var(--primary-color);
  color: white;
}
</style>