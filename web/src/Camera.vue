<template>
  <div class="camera-page">
    <h2 class="page-title">
      <span class="camera-icon">📷</span> 虚拟摄像头
    </h2>
    
    <div class="preview-container">
      <div class="preview-label">实时虚拟摄像头画面</div>
    </div>
    
    <div class="camera-controls">
      <div class="control-group">
        <label>
          <span class="control-label">推流</span>
          <input type="checkbox" class="toggle-switch" checked>
        </label>
      </div>
      
      <div class="control-group">
        <label>
          <span class="control-label">摄像头背景</span>
          <input type="checkbox" class="toggle-switch">
        </label>
      </div>
      
      <div class="control-group">
        <label>
          <span class="control-label">设置虚拟摄像头名称:</span>
          <input type="text" class="name-input" placeholder="Live2D_Cam">
        </label>
      </div>
    </div>
  </div>
</template>

<style scoped>
.camera-page {
  padding: 20px;
  color: white;
}

.page-title {
  display: flex;
  align-items: center;
  font-size: 24px;
  margin-bottom: 20px;
}

.camera-icon {
  margin-right: 10px;
}

.preview-container {
  height: 300px;
  background: #1e1e1e;
  border-radius: 8px;
  margin-bottom: 20px;
  position: relative;
  border: 2px solid #444;
}

.preview-label {
  position: absolute;
  top: 5px;
  left: 5px;
  background: rgba(0,0,0,0.5);
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 10;
}

.camera-controls {
  background: #2d2d2d;
  border-radius: 8px;
  padding: 20px;
}

.control-group {
  margin-bottom: 15px;
}

.control-label {
  display: inline-block;
  width: 150px;
}

.toggle-switch {
  position: relative;
  width: 60px;
  height: 30px;
  -webkit-appearance: none;
  background: #444;
  border-radius: 30px;
  transition: all 0.3s;
}

.toggle-switch:checked {
  background: #42b983;
}

.toggle-switch::before {
  content: '';
  position: absolute;
  width: 22px;
  height: 22px;
  background: white;
  border-radius: 50%;
  top: 4px;
  left: 4px;
  transition: all 0.3s;
}

.toggle-switch:checked::before {
  left: 34px;
}

.name-input {
  padding: 8px 12px;
  background: #1e1e1e;
  border: 1px solid #444;
  border-radius: 4px;
  color: white;
  width: 200px;
}
</style>