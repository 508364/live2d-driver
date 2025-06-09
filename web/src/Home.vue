<template>
  <div class="home-page">
    <h2 class="page-title">
      <span class="home-icon">🏠</span> 首页
    </h2>
    
    <div class="status-card">
      <span class="status-icon">●</span>
      <span class="status-text">Live2D形象状态</span>
    </div>
    
    <button class="track-button">
      <span>启动面捕、动捕</span>
    </button>
    
    <div class="fps-display">
      <span class="fps-label">实时FPS: </span>
      <span class="fps-value">--</span>
    </div>
    
    <div class="camera-preview">
      <div class="preview-label">实时摄像头画面</div>
    </div>
    
    <div class="model-preview">
      <div class="preview-label">Live2D形象预览</div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  padding: 20px;
  color: white;
}

.page-title {
  display: flex;
  align-items: center;
  font-size: 24px;
  margin-bottom: 20px;
}

.home-icon {
  margin-right: 10px;
}

.status-card {
  background: #2d2d2d;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 16px;
  display: flex;
  align-items: center;
  border-left: 3px solid #42b983;
}

.status-icon {
  color: #42b983;
  margin-right: 10px;
  font-size: 20px;
}

.track-button {
  background: #42b983;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 20px;
  width: 200px;
}

.fps-display {
  margin-bottom: 20px;
  color: #42b983;
  font-weight: bold;
}

.camera-preview, .model-preview {
  border: 2px solid #444;
  border-radius: 8px;
  height: 200px;
  margin-bottom: 20px;
  background: #1e1e1e;
  position: relative;
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
</style>