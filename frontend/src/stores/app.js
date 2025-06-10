import { defineStore } from 'pinia';
import axios from 'axios';
import { ref, computed } from 'vue';

export const useAppStore = defineStore('app', () => {
  // 状态变量
  const videoDevices = ref([]);
  const selectedDevice = ref(null);
  const isTracking = ref(false);
  const isCameraActive = ref(false);
  const isLoading = ref(false);
  const faceDetected = ref(false);
  const live2dModels = ref([]);
  const selectedModel = ref(null);
  const position = ref({ x: 0, y: 0, z: 0 });
  const expression = ref('neutral');
  const webSocket = ref(null);
  const stream = ref(null);
  const serverStatus = ref('disconnected');
  
  // Getters
  const activeDeviceName = computed(() => {
    return videoDevices.value.find(d => d.deviceId === selectedDevice.value)?.label || '';
  });

  const modelNames = computed(() => {
    return live2dModels.value.map(model => model.name);
  });

  // Actions
  const detectDevices = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      videoDevices.value = devices.filter(d => d.kind === 'videoinput');
      
      if (videoDevices.value.length > 0 && !selectedDevice.value) {
        selectedDevice.value = videoDevices.value[0].deviceId;
      }
    } catch (error) {
      console.error('无法获取视频设备:', error);
      videoDevices.value = [];
    }
  };

  const setupWebcam = async () => {
    try {
      const constraints = selectedDevice.value ? 
        { video: { deviceId: selectedDevice.value } } : 
        { video: true };
        
      stream.value = await navigator.mediaDevices.getUserMedia(constraints);
      isCameraActive.value = true;
      return stream.value;
    } catch (error) {
      console.error('无法访问摄像头:', error);
      isCameraActive.value = false;
      return null;
    }
  };

  const connectToServer = () => {
    serverStatus.value = 'connecting';
    const backendUrl = process.env.VUE_APP_BACKEND_URL || `ws://${window.location.hostname}:8080`;
    
    try {
      // 初始化WebSocket连接
      webSocket.value = new WebSocket(`${backendUrl}/ws`);
      
      webSocket.value.onopen = () => {
        serverStatus.value = 'connected';
        console.log('成功连接到后端服务器');
      };
      
      webSocket.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleServerMessage(data);
        } catch (e) {
          console.error('无法解析消息:', event.data);
        }
      };
      
      webSocket.value.onclose = () => {
        serverStatus.value = 'disconnected';
        console.log('服务器连接已关闭');
      };
      
      webSocket.value.onerror = (error) => {
        serverStatus.value = 'error';
        console.error('WebSocket错误:', error);
      };
    } catch (error) {
      console.error('连接服务器失败:', error);
      serverStatus.value = 'error';
    }
  };

  const handleServerMessage = (data) => {
    switch (data.type) {
      case 'face_data':
        position.value = data.position;
        expression.value = data.expression;
        faceDetected.value = true;
        break;
      
      case 'models_list':
        live2dModels.value = data.models;
        break;
      
      case 'error':
        console.error('服务器错误:', data.message);
        break;
        
      default:
        console.warn('未知消息类型:', data.type);
    }
  };

  const toggleTracking = async () => {
    if (!isTracking.value) {
      if (!stream.value && !(await setupWebcam())) return;
      
      if (!webSocket.value || webSocket.value.readyState !== WebSocket.OPEN) {
        connectToServer();
      }
      
      isLoading.value = true;
      try {
        // 发送初始化命令
        webSocket.value.send(JSON.stringify({ 
          command: 'start_tracking', 
          camera_source: 'webcam' 
        }));
        
        isTracking.value = true;
        isLoading.value = false;
        console.log('面部追踪已启动');
      } catch (error) {
        console.error('启动面部追踪失败:', error);
        isLoading.value = false;
      }
    } else {
      // 停止追踪
      try {
        webSocket.value.send(JSON.stringify({ 
          command: 'stop_tracking' 
        }));
        
        isTracking.value = false;
        faceDetected.value = false;
        console.log('面部追踪已停止');
      } catch (error) {
        console.error('停止面部追踪失败:', error);
      }
    }
  };

  const loadModels = async () => {
    if (live2dModels.value.length > 0) return;
    
    try {
      const response = await axios.get('/api/models');
      live2dModels.value = response.data;
      console.log('Live2D模型已加载:', live2dModels.value);
    } catch (error) {
      console.error('加载Live2D模型失败:', error);
    }
  };

  const switchModel = (modelName) => {
    if (!live2dModels.value.some(m => m.name === modelName)) {
      console.warn('无效的模型名称:', modelName);
      return;
    }
    
    selectedModel.value = modelName;
    
    if (webSocket.value?.readyState === WebSocket.OPEN) {
      webSocket.value.send(JSON.stringify({ 
        command: 'switch_model', 
        model: modelName 
      }));
    }
  };

  const switchExpression = (expr) => {
    expression.value = expr;
    
    if (webSocket.value?.readyState === WebSocket.OPEN) {
      webSocket.value.send(JSON.stringify({ 
        command: 'expression', 
        expression: expr 
      }));
    }
  };

  const switchPosition = (pos) => {
    position.value = pos;
    
    if (webSocket.value?.readyState === WebSocket.OPEN) {
      webSocket.value.send(JSON.stringify({ 
        command: 'position', 
        position: pos 
      }));
    }
  };

  // 初始化和清理
  const initializeApp = async () => {
    await Promise.all([detectDevices(), loadModels()]);
  };

  const cleanup = () => {
    if (webSocket.value && webSocket.value.readyState !== WebSocket.CLOSED) {
      webSocket.value.close();
    }
    
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop());
      stream.value = null;
    }
    
    isCameraActive.value = false;
    isTracking.value = false;
  };

  // 自动初始化
  initializeApp();

  return {
    // 状态变量
    videoDevices,
    selectedDevice,
    isTracking,
    isCameraActive,
    isLoading,
    faceDetected,
    live2dModels,
    selectedModel,
    position,
    expression,
    serverStatus,
    
    // Getters
    activeDeviceName,
    modelNames,
    
    // Actions
    detectDevices,
    setupWebcam,
    connectToServer,
    toggleTracking,
    loadModels,
    switchModel,
    switchExpression,
    switchPosition,
    initializeApp,
    cleanup
  };
});