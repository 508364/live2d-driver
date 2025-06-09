import cv2

class Camera:
    def __init__(self, index=0, width=1280, height=720, fps=30):
        self.cap = cv2.VideoCapture(index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.width = width
        self.height = height
        self.fps = fps
        
    def get_frame(self):
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
        
    def release(self):
        if self.cap.isOpened():
            self.cap.release()
            
    def is_open(self):
        return self.cap.isOpened()