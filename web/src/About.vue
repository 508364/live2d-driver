<template>
  <div class="about-page">
    <h2 class="page-title">
      <span class="about-icon">ℹ️</span> 关于
    </h2>
    
    <div class="app-info">
      <h3>Live2D驱动器 Beta</h3>
      <p>版本: 1.0.0</p>
      <p>基于 Electron + Vue.js + OpenCV 构建</p>
      <p>协议: CC BY-NC-SA 4.0</p>
    </div>
    
    <div class="links">
      <button class="link-btn">GitHub</button>
      <button class="link-btn">Live2D官网</button>
    </div>
  </div>
</template>

<style scoped>
.about-page {
  padding: 20px;
  color: white;
  text-align: center;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 30px;
}

.about-icon {
  margin-right: 10px;
}

.app-info {
  background: #2d2d2d;
  border-radius: 8px;
  padding: 30px;
  margin-bottom: 30px;
}

.app-info h3 {
  font-size: 24px;
  margin-bottom: 15px;
  color: #42b983;
}

.app-info p {
  margin: 10px 0;
  color: #aaa;
}

.links {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.link-btn {
  padding: 10px 25px;
  background: rgba(66, 185, 131, 0.2);
  border: 1px solid #42b983;
  border-radius: 6px;
  color: #42b983;
  cursor: pointer;
  font-weight: bold;
}

.link-btn:hover {
  background: rgba(66, 185, 131, 0.3);
}
</style>