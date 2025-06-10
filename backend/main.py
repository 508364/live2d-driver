import os
import sys
import json
import asyncio
import logging
import time
import threading
import webbrowser
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('backend.log')
    ]
)

class BackendServer:
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.frontend_started = False
        self.logs = []
        
    def log(self, message, level='info'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'message': message,
            'level': level
        }
        self.logs.append(log_entry)
        getattr(logging, level)(message)
        
        # 保持日志大小
        if len(self.logs) > 500:
            self.logs.pop(0)
    
    def start(self):
        if self.is_running:
            return False
            
        self.is_running = True
        self.log("后端服务器启动中...")
        
        # 启动前端线程
        frontend_thread = threading.Thread(target=self.start_frontend)
        frontend_thread.daemon = True
        frontend_thread.start()
        
        # 启动虚拟摄像头线程
        virtual_camera_thread = threading.Thread(target=self.start_virtual_camera)
        virtual_camera_thread.daemon = True
        virtual_camera_thread.start()
        
        self.thread = threading.Thread(target=self.run_server)
        self.thread.daemon = True
        self.thread.start()
        
        return True
        
    def stop(self):
        if not self.is_running:
            return
            
        self.is_running = False
        self.log("后端服务器正在停止...")
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)
            
        self.log("后端服务器已停止")
        
    def run_server(self):
        # 模拟服务器运行
        while self.is_running:
            if self.frontend_started and not webbrowser.get().open('http://localhost:3000'):
                self.log("自动打开浏览器失败，请手动访问 http://localhost:3000", "warning")
            else:
                self.log("前端已在浏览器中打开")
                
            # 每5秒记录一次状态
            self.log("后端服务器运行中...")
            for _ in range(5):
                if not self.is_running:
                    break
                time.sleep(1)
                
    def start_frontend(self):
        # 启动前端开发服务器
        self.log("启动前端开发服务器...")
        
        # 模拟前端启动
        time.sleep(3)
        self.frontend_started = True
        self.log("前端开发服务器已启动 (http://localhost:3000)")
        
    def start_virtual_camera(self):
        # 启动虚拟摄像头
        self.log("启动虚拟摄像头...")
        
        # 模拟虚拟摄像头运行
        try:
            # 在实际项目中会调用虚拟摄像头模块
            from virtual_camera import VirtualCamera
            vcam = VirtualCamera()
            if vcam.start():
                self.log("虚拟摄像头启动成功")
            else:
                self.log("虚拟摄像头启动失败", "error")
        except ImportError:
            self.log("虚拟摄像头模块不可用", "error")
            
        # 模拟虚拟摄像头运行日志
        while self.is_running:
            self.log("虚拟摄像头工作中...")
            time.sleep(10)
            
    def get_logs(self):
        return self.logs