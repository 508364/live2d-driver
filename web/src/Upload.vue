<template>
  <div class="upload-page">
    <h2 class="page-title">上传live2d形象</h2>
    
    <div class="upload-area">
      <div class="upload-hint">
        <span class="upload-icon">📁</span>
        <p>点击或拖放文件夹/.zip文件到此处</p>
      </div>
    </div>
    
    <div class="model-list">
      <div class="model-item">
        <div class="model-info">
          <h3>Haru</h3>
          <p>4.07 MB</p>
        </div>
        <button class="use-model-btn">
          <span class="star">★</span> 使用形象
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-page {
  padding: 20px;
  color: white;
}

.page-title {
  font-size: 24px;
  margin-bottom: 20px;
}

.upload-area {
  border: 2px dashed #42b983;
  border-radius: 8px;
  padding: 60px 20px;
  text-align: center;
  margin-bottom: 30px;
  background: rgba(66, 185, 131, 0.1);
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
  background: #1e1e1e;
  border-radius: 8px;
  padding: 20px;
}

.model-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #444;
}

.model-item:last-child {
  border-bottom: none;
}

.model-info {
  flex: 1;
}

.model-info h3 {
  margin: 0;
  font-size: 18px;
}

.model-info p {
  margin: 5px 0 0 0;
  color: #aaa;
  font-size: 14px;
}

.use-model-btn {
  background: #42b983;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.star {
  color: gold;
  margin-right: 5px;
}
</style>