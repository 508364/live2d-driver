import asyncio
import json
import websockets
import cv2
import numpy as np
import sys
from camera import Camera
from virtual_camera import VirtualCamera
from stream import VideoStreamServer

class Live2DDriver:
    def __init__(self):
        self.camera = None
        self.virtual_cam = None
        self.stream_server = VideoStreamServer(port=9000)
        self.running = False
        self.clients = set()
        
    async def handle_client(self, websocket, path):
        self.clients.add(websocket)
        print(f"New client connected: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                data = json.loads(message)
                command = data.get('command')
                
                if command == 'start_tracking':
                    self.start_tracking()
                elif command == 'stop_tracking':
                    self.stop_tracking()
                elif command == 'set_model':
                    model_path = data.get('path')
                    print(f"Setting model to: {model_path}")
                elif command == 'get_config':
                    # 返回模拟配置
                    config = {
                        "camera": {"resolution": "1280x720", "fps": 30},
                        "model": {"default": "Haru"}
                    }
                    await websocket.send(json.dumps(config))
                    
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
        finally:
            self.clients.remove(websocket)
            self.stop_tracking()
    
    def start_tracking(self):
        if self.running:
            return
            
        self.running = True
        self.camera = Camera(0)
        self.virtual_cam = VirtualCamera()
        self.stream_server.start()
        
        # 启动处理循环
        asyncio.create_task(self.process_frames())
        
    def stop_tracking(self):
        if not self.running:
            return
            
        self.running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        if self.virtual_cam:
            self.virtual_cam.release()
            self.virtual_cam = None
        self.stream_server.stop()
        
    async def process_frames(self):
        frame_count = 0
        last_time = time.time()
        
        while self.running:
            frame = self.camera.get_frame()
            if frame is None:
                await asyncio.sleep(0.01)
                continue
                
            # 进行面部检测
            faces = self.detect_faces(frame)
            
            # 发送到所有客户端
            for client in self.clients:
                await client.send(json.dumps({
                    "type": "face_data",
                    "data": faces
                }))
                
            # 处理FPS
            frame_count += 1
            current_time = time.time()
            if current_time - last_time >= 1.0:
                fps = frame_count / (current_time - last_time)
                for client in self.clients:
                    await client.send(json.dumps({
                        "type": "fps",
                        "data": fps
                    }))
                frame_count = 0
                last_time = current_time
                
            # 更新虚拟摄像头
            self.virtual_cam.push_frame(frame)
            
            # 视频流输出
            self.stream_server.push_frame(frame)
            
            await asyncio.sleep(0.01)
    
    def detect_faces(self, frame):
        # 简单面部检测
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        results = []
        for (x, y, w, h) in faces:
            results.append({
                "x": int(x), 
                "y": int(y),
                "width": int(w),
                "height": int(h),
                "center_x": int(x + w/2),
                "center_y": int(y + h/2)
            })
            
        return results

async def main():
    driver = Live2DDriver()
    server = await websockets.serve(driver.handle_client, "localhost", 50836)
    print("Live2D Driver Server running at ws://localhost:50836")
    
    try:
        await asyncio.Future()  # 永久运行
    except asyncio.CancelledError:
        pass
    finally:
        server.close()
        driver.stop_tracking()

if __name__ == "__main__":
    asyncio.run(main())