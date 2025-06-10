# Live2D驱动器

一个基于人工智能的面部捕捉软件，可将实时面部表情映射到Live2D模型上，并提供虚拟摄像头功能。

## 功能特点

- **实时面部捕捉**：使用TensorFlow.js实现高效的面部表情识别
- **Live2D模型支持**：兼容各种Live2D模型格式
- **虚拟摄像头**：将模型输出转化为虚拟摄像头源，兼容各种视频会议软件
- **多主题支持**：提供深色、浅色和自定义主题
- **完整日志系统**：记录所有操作，支持日志导出

## 系统要求

- **操作系统**：Windows 10/11, macOS 10.15+, Linux (基于Ubuntu 20.04+)
- **Python**：3.8 或更高版本
- **Node.js**：16.x 或更高版本

## 安装指南

### 1. 安装依赖

1. **安装依赖**：
```bash
cd frontend
npm install

cd ../backend
pip install -r requirements.txt

2. **​​启动应用程序​​**
python run.py