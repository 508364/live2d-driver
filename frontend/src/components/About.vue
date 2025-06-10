<template>
  <div class="about-page">
    <div class="app-info">
      <h1 class="app-name">Live2D驱动器</h1>
      <p class="version">版本: 1.0.0-beta</p>
      <p class="tech-stack">基于Electron + Vue.js + TensorFlow.js + Python构建</p>
      <p class="license">协议: CC BY-NC-SA 4.0</p>
    </div>
    
    <div class="feature-list">
      <div class="feature">
        <div class="feature-icon">🎭</div>
        <h3>实时面部捕捉</h3>
        <p>使用深度学习技术精确捕捉面部表情</p>
      </div>
      
      <div class="feature">
        <div class="feature-icon">📹</div>
        <h3>虚拟摄像头</h3>
        <p>将Live2D模型输出为虚拟摄像头源</p>
      </div>
      
      <div class="feature">
        <div class="feature-icon">🔄</div>
        <h3>多模型支持</h3>
        <p>支持各种格式的Live2D模型</p>
      </div>
    </div>
    
    <div class="documentation">
      <h2>相关链接</h2>
      <div class="links">
        <a href="https://live2d.com" class="link-btn" @click.prevent="openLive2D">Live2D官网</a>
        <a href="https://github.com/508364/live2d-driver" class="link-btn" @click.prevent="openGitHub">GitHub项目</a>
        <a href="https://en.wikipedia.org/wiki/CC_BY-NC-SA_4.0" class="link-btn" @click.prevent="openLicense">许可证说明</a>
      </div>
    </div>
    
    <div class="copyright">
      <p>© 2023 Live2D驱动器项目组。保留部分权利。</p>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    openLive2D() {
      window.open('https://live2d.com', '_blank')
    },
    
    openGitHub() {
      window.open('https://github.com/508364/live2d-driver', '_blank')
    },
    
    openLicense() {
      window.open('https://en.wikipedia.org/wiki/CC_BY-NC-SA_4.0', '_blank')
    }
  }
}
</script>

<style scoped>
.about-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.app-info {
  text-align: center;
  margin-bottom: 30px;
}

.app-name {
  font-size: 32px;
  color: var(--primary-color);
  margin-bottom: 10px;
}

.version {
  font-size: 18px;
  color: #aaa;
  margin-bottom: 5px;
}

.tech-stack {
  margin-bottom: 5px;
}

.license {
  color: #42b983;
  font-weight: 500;
}

.feature-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.feature {
  background: var(--card-bg);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.feature-icon {
  font-size: 40px;
  margin-bottom: 15px;
}

.feature h3 {
  margin: 0 0 10px;
  font-size: 20px;
}

.feature p {
  color: #aaa;
  margin: 0;
}

.documentation {
  margin-bottom: 30px;
}

.documentation h2 {
  text-align: center;
  font-size: 24px;
  margin-bottom: 20px;
}

.links {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.link-btn {
  display: inline-block;
  padding: 12px 25px;
  background: rgba(66, 185, 131, 0.1);
  border: 1px solid var(--primary-color);
  border-radius: 6px;
  color: var(--primary-color);
  text-decoration: none;
  transition: all 0.3s;
  cursor: pointer;
}

.link-btn:hover {
  background: var(--primary-color);
  color: white;
  transform: translateY(-3px);
}

.copyright {
  text-align: center;
  color: #666;
  margin-top: auto;
  padding: 20px 0;
}
</style>