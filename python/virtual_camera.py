import cv2
import numpy as np
try:
    import pyvirtualcam
except ImportError:
    # 处理虚拟摄像头不可用的情况
    pyvirtualcam = None

class VirtualCamera:
    def __init__(self, width=1280, height=720, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.cam = None
        
        if pyvirtualcam:
            try:
                self.cam = pyvirtualcam.Camera(width, height, fps, fmt='bgr')
                print(f"Virtual camera created: {self.cam.device}")
            except Exception as e:
                print(f"Failed to create virtual camera: {e}")
                self.cam = None
        
    def push_frame(self, frame):
        if self.cam:
            try:
                # 调整帧大小以匹配虚拟摄像头
                resized = cv2.resize(frame, (self.width, self.height))
                self.cam.send(resized)
                self.cam.sleep_until_next_frame()
            except Exception as e:
                print(f"Error sending frame to virtual camera: {e}")
                
    def release(self):
        if self.cam:
            self.cam.close()
            
    def is_open(self):
        return self.cam is not None